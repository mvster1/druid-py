#!/usr/bin/env python3
# druid - batch image resizer.

import ctypes
import os
import queue
import sys
import threading
import time
import winreg
from ctypes import wintypes

PIPE = r"\\.\pipe\druid"
DIR = os.path.dirname(os.path.abspath(__file__))
EXTS = (".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff",
        ".gif", ".avif", ".heic", ".jxl", ".bmp", ".ppm", ".pgm")
MAX = 10 ** 7

# context menu verb. "image" covers every file whose PerceivedType is image;
# the extensions after it have no perceived type and need their own key.
KEY = r"Software\Classes\SystemFileAssociations\%s\shell\druid.resize"
TYPES = ("image", ".jxl", ".ppm", ".pgm")
PYW = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
if not os.path.exists(PYW):
    PYW = sys.executable
CMD = '"%s" "%s" --resize "%%1"' % (PYW, os.path.join(DIR, "druid.py"))

# PIPE_ACCESS_DUPLEX | FILE_FLAG_FIRST_PIPE_INSTANCE: creating the pipe fails
# when another druid already holds it, which is also the single instance lock.
OPEN_MODE = 0x00000003 | 0x00080000
INVALID = ctypes.c_void_p(-1).value
K32 = ctypes.WinDLL("kernel32", use_last_error=True)
K32.CreateNamedPipeW.restype = wintypes.HANDLE
K32.CreateNamedPipeW.argtypes = [wintypes.LPCWSTR] + [wintypes.DWORD] * 6 + [wintypes.LPVOID]
K32.ConnectNamedPipe.argtypes = [wintypes.HANDLE, wintypes.LPVOID]
K32.DisconnectNamedPipe.argtypes = [wintypes.HANDLE]
K32.ReadFile.argtypes = [wintypes.HANDLE, wintypes.LPVOID, wintypes.DWORD,
                         ctypes.POINTER(wintypes.DWORD), wintypes.LPVOID]

files = []

def client(msg):
    # explorer runs this once per selected file, so it must stay cheap:
    # no pyvips, no tkinter. it only hands the path to the running druid.
    for _ in range(80):
        try:
            with open(PIPE, "r+b", buffering=0) as f:
                f.write(msg.encode() + b"\n")
            return
        except FileNotFoundError:
            return              # no druid listening, nothing to hand over
        except OSError:
            time.sleep(0.02)    # the single pipe instance is busy, wait a turn

def dim(var):
    s = var.get().strip()
    if not s:
        return 0
    n = int(s)
    if n < 1:
        raise ValueError(s)
    return n

def resize(src, out, w, h, keep):
    if keep:
        im = pyvips.Image.thumbnail(src, w or MAX, height=h or MAX)
    else:
        im = pyvips.Image.thumbnail(src, w, height=h, size="force")
    base, ext = os.path.splitext(os.path.basename(src))
    dst = os.path.join(out or os.path.dirname(src),
                       f"{base}___{im.width}x{im.height}{ext}")
    im.write_to_file(dst)
    return dst

def batch(paths, out, w, h, keep):
    ok, err = 0, ""
    for src in paths:
        try:
            resize(src, out, w, h, keep)
            ok += 1
        except Exception as e:
            err = err or "%s: %s" % (os.path.basename(src), e)
    return ok, err

def label(w, h, keep):
    if not keep:
        return "resize selected images to %dx%d" % (w, h)
    if w and h:
        return "resize selected images to fit %dx%d" % (w, h)
    return "resize selected images to fit %d %s" % (w or h,
                                                    "wide" if w else "tall")

def flush_shell():
    # SHCNE_ASSOCCHANGED, SHCNF_IDLIST | SHCNF_FLUSHNOWAIT
    ctypes.windll.shell32.SHChangeNotify(0x08000000, 0x3000, None, None)

def verb(text):
    for t in TYPES:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, KEY % t) as k:
            winreg.SetValueEx(k, "MUIVerb", 0, winreg.REG_SZ, text)
            winreg.SetValueEx(k, "Icon", 0, winreg.REG_SZ,
                              os.path.join(DIR, "icon.ico"))
            winreg.SetValueEx(k, "MultiSelectModel", 0, winreg.REG_SZ, "Player")
            winreg.SetValue(k, "command", winreg.REG_SZ, CMD)
    flush_shell()

def unverb():
    for t in TYPES:
        for sub in (KEY % t + r"\command", KEY % t):
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, sub)
            except OSError:
                pass
    flush_shell()

def serve(h, q):
    # daemon thread: it blocks in ConnectNamedPipe until a client shows up and
    # dies with the process. closing the handle here would hang instead - a
    # synchronous ConnectNamedPipe pending on another thread blocks CloseHandle.
    buf = ctypes.create_string_buffer(4096)
    n = wintypes.DWORD()
    while True:
        K32.ConnectNamedPipe(h, None)
        if K32.ReadFile(h, buf, 4096, ctypes.byref(n), None):
            msg = buf.raw[:n.value].decode("utf-8", "replace").strip()
            if msg:
                q.put(msg)
        K32.DisconnectNamedPipe(h)

def main():
    # heavy imports live here so that --resize never pays for them.
    global pyvips
    import pyvips
    import tkinter as tk
    from tkinter import filedialog, ttk
    import pystray
    from PIL import Image

    try:
        from tkinterdnd2 import DND_FILES, TkinterDnD
    except ImportError:
        TkinterDnD = None

    pipe = K32.CreateNamedPipeW(PIPE, OPEN_MODE, 0, 255, 4096, 4096, 0, None)

    if pipe == INVALID:
        return client("show")   # another druid owns the pipe, wake it instead

    root = TkinterDnD.Tk() if TkinterDnD else tk.Tk()
    root.title("druid")
    root.minsize(420, 300)

    icon = os.path.join(DIR, "icon.png")
    if os.path.exists(icon):
        root.png = tk.PhotoImage(file=icon)
        root.iconphoto(True, root.png)

    top = ttk.Frame(root, padding=8)
    top.grid(row=0, column=0, sticky="ew")
    mid = ttk.Frame(root, padding=(8, 0))
    mid.grid(row=1, column=0, sticky="nsew")
    bot = ttk.Frame(root, padding=8)
    bot.grid(row=2, column=0, sticky="ew")
    root.rowconfigure(1, weight=1)
    root.columnconfigure(0, weight=1)
    mid.rowconfigure(0, weight=1)
    mid.columnconfigure(0, weight=1)

    wvar, hvar = tk.StringVar(), tk.StringVar()
    ttk.Label(top, text="width").grid(row=0, column=0, sticky="w")
    ttk.Entry(top, width=7, textvariable=wvar).grid(row=0, column=1, padx=(4, 12))
    ttk.Label(top, text="height").grid(row=0, column=2, sticky="w")
    ttk.Entry(top, width=7, textvariable=hvar).grid(row=0, column=3, padx=(4, 12))
    keep = tk.BooleanVar(value=False)
    ttk.Checkbutton(top, text="keep aspect ratio",
                    variable=keep, cursor="hand2").grid(row=0, column=4, sticky="w")

    box = tk.Listbox(mid, activestyle="none", highlightthickness=0)
    box.grid(row=0, column=0, sticky="nsew")
    bar = ttk.Scrollbar(mid, orient="vertical", command=box.yview)
    bar.grid(row=0, column=1, sticky="ns")
    box.configure(yscrollcommand=bar.set)

    def hover(e):
        b = box.bbox(box.nearest(e.y))
        over = b and b[1] <= e.y < b[1] + b[3]
        box.configure(cursor="hand2" if over else "")

    box.bind("<Motion>", hover)
    box.bind("<Leave>", lambda e: box.configure(cursor=""))

    status = ttk.Label(bot, text="no images")
    status.grid(row=1, column=0, columnspan=3, sticky="w", pady=(6, 0))

    def say(msg):
        status.configure(text=msg)

    def spec():
        try:
            w, h = dim(wvar), dim(hvar)
        except ValueError:
            raise ValueError("width and height must be positive integers") from None
        if keep.get():
            if not (w or h):
                raise ValueError("enter width or height")
        elif not (w and h):
            raise ValueError("enter width and height")
        return w, h, keep.get()

    def add(paths):
        n = 0
        for p in paths:
            p = os.path.abspath(p)
            if p.lower().endswith(EXTS) and p not in files:
                files.append(p)
                box.insert("end", os.path.basename(p))
                n += 1
        say("%d images" % len(files) if files else "no images")
        if paths and not n:
            say("no new images")

    def pick():
        add(filedialog.askopenfilenames(
            title="select images",
            filetypes=[("images", " ".join("*" + e for e in EXTS)),
                       ("all files", "*.*")]))

    def clear():
        files.clear()
        box.delete(0, "end")
        say("no images")

    def run():
        if not files:
            return say("select at least one image")
        try:
            w, h, k = spec()
        except ValueError as e:
            return say(str(e))
        out = filedialog.askdirectory(title="where to save the images")
        if not out:
            return
        ok, err = batch(files, out, w, h, k)
        say("%d of %d resized%s" % (ok, len(files), "  -  " + err if err else ""))

    ttk.Button(bot, text="select images",
               command=pick, cursor="hand2").grid(row=0, column=0)
    ttk.Button(bot, text="clear", command=clear,
               cursor="hand2").grid(row=0, column=1, padx=6)
    ttk.Button(bot, text="resize",
               command=run, cursor="hand2").grid(row=0, column=2, sticky="e")
    bot.columnconfigure(2, weight=1)

    if TkinterDnD:
        box.drop_target_register(DND_FILES)
        box.dnd_bind("<<Drop>>", lambda e: add(root.tk.splitlist(e.data)))
        say("drop images here or click select images")

    q = queue.Queue()
    ico = pystray.Icon(
        "druid", Image.open(icon).resize((64, 64)), "druid",
        pystray.Menu(pystray.MenuItem("show", lambda *_: q.put("show"), default=True),
                     pystray.MenuItem("quit", lambda *_: q.put("quit"))))

    def show():
        root.deiconify()
        root.lift()
        root.focus_force()

    def bye():
        unverb()
        ico.stop()
        root.destroy()

    # the context menu entry exists only while druid runs and the fields hold a
    # valid request, so it is rewritten on every change and dropped on exit.
    job = {"verb": None, "flush": None}

    def sync(*_):
        if job["verb"]:
            root.after_cancel(job["verb"])
        job["verb"] = root.after(400, register)

    def register():
        job["verb"] = None
        try:
            w, h, k = spec()
        except ValueError:
            return unverb()
        verb(label(w, h, k))

    # explorer invokes the verb once per file; collect them into one batch.
    pending = []

    def flush():
        job["flush"] = None
        paths, pending[:] = pending[:], []
        try:
            w, h, k = spec()
        except ValueError:
            return
        ok, err = batch(paths, None, w, h, k)
        say("%d of %d resized%s" % (ok, len(paths), "  -  " + err if err else ""))

    def poll():
        try:
            while True:
                msg = q.get_nowait()
                if msg == "show":
                    show()
                    continue
                if msg == "quit":
                    return bye()
                pending.append(msg)
                if job["flush"]:
                    root.after_cancel(job["flush"])
                job["flush"] = root.after(400, flush)
        except queue.Empty:
            pass
        root.after(120, poll)

    threading.Thread(target=serve, args=(pipe, q), daemon=True).start()
    threading.Thread(target=ico.run, daemon=True).start()

    for v in (wvar, hvar, keep):
        v.trace_add("write", sync)
    unverb()            # drop a stale entry left behind by a crash
    root.protocol("WM_DELETE_WINDOW", bye)
    root.after(120, poll)
    root.mainloop()

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--resize":
        client(os.path.abspath(sys.argv[2]))
    else:
        main()
