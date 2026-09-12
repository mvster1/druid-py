#!/usr/bin/env python3
# druid - batch image resizer.

import os
import tkinter as tk
from tkinter import filedialog, ttk

import pyvips

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:
    TkinterDnD = None

DIR = os.path.dirname(os.path.abspath(__file__))
EXTS = (".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff",
        ".gif", ".avif", ".heic", ".jxl", ".bmp", ".ppm", ".pgm")
MAX = 10 ** 7

files = []


def dim(entry):
    s = entry.get().strip()
    if not s:
        return 0
    n = int(s)
    if n < 1:
        raise ValueError(s)
    return n


def resize(src, dst, w, h, keep):
    if keep:
        im = pyvips.Image.thumbnail(src, w or MAX, height=h or MAX)
    else:
        im = pyvips.Image.thumbnail(src, w, height=h, size="force")
    im.write_to_file(dst)


def main():
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

    ttk.Label(top, text="width").grid(row=0, column=0, sticky="w")
    width = ttk.Entry(top, width=7)
    width.grid(row=0, column=1, padx=(4, 12))
    ttk.Label(top, text="height").grid(row=0, column=2, sticky="w")
    height = ttk.Entry(top, width=7)
    height.grid(row=0, column=3, padx=(4, 12))
    keep = tk.BooleanVar(value=False)
    ttk.Checkbutton(top, text="keep aspect ratio",
                    variable=keep, cursor="hand2").grid(row=0, column=4, sticky="w")

    box = tk.Listbox(mid, activestyle="none", highlightthickness=0)
    box.grid(row=0, column=0, sticky="nsew")
    bar = ttk.Scrollbar(mid, orient="vertical", command=box.yview)
    bar.grid(row=0, column=1, sticky="ns")
    box.configure(yscrollcommand=bar.set)

    status = ttk.Label(bot, text="no images")
    status.grid(row=1, column=0, columnspan=3, sticky="w", pady=(6, 0))

    def say(msg):
        status.configure(text=msg)

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
            w, h = dim(width), dim(height)
        except ValueError:
            return say("width and height must be positive integers")
        if keep.get():
            if not (w or h):
                return say("enter width or height")
        elif not (w and h):
            return say("enter width and height")

        out = filedialog.askdirectory(title="where to save the images")
        if not out:
            return
        ok, err = 0, ""
        for src in files:
            name, ext = os.path.splitext(os.path.basename(src))
            dst = os.path.join(out, name + ext)
            if os.path.abspath(dst) == src:
                dst = os.path.join(out, "%s-%dx%d%s" % (name, w, h, ext))
            try:
                resize(src, dst, w, h, keep.get())
                ok += 1
            except Exception as e:
                err = err or "%s: %s" % (os.path.basename(src), e)
        say("%d of %d resized%s" % (ok, len(files),
                                    "  -  " + err if err else ""))

    ttk.Button(bot, text="select images",
               command=pick, cursor="hand2").grid(row=0, column=0)
    ttk.Button(bot, text="clear", command=clear, cursor="hand2").grid(row=0, column=1, padx=6)
    ttk.Button(bot, text="resize",
               command=run, cursor="hand2").grid(row=0, column=2, sticky="e")
    bot.columnconfigure(2, weight=1)

    if TkinterDnD:
        box.drop_target_register(DND_FILES)
        box.dnd_bind("<<Drop>>", lambda e: add(root.tk.splitlist(e.data)))
        say("drop images here or use select images")

    root.mainloop()


if __name__ == "__main__":
    main()
