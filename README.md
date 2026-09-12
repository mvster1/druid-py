<img src="icon.png" alt="druid" width="128">

## druid

druid is a batch image resizer. all in one file, no configuration necessary.

### dependencies

    pip install "pyvips[binary]" tkinterdnd2 pystray

`tkinterdnd2` is optional: without it dragging and dropping images doesn't work, the rest works.

### usage

    python druid.py        # or pythonw druid.py, no console window

1. drop images onto the list or click `select images`
2. fill in `width` and/or `height`
3. `resize` asks where to save

with `keep aspect ratio` the image fits inside the width x height box and
only one of the two is required. without it, both are required and the
image is forced to the exact size.

the output format follows the original file extension, and every file gets a
`___WIDTHxHEIGHT` suffix naming the size it came out as - so nothing ever
overwrites its own original.

while druid runs its icon sits in the tray, and clicking it brings the window
back. minimizing behaves like any other app; the X quits druid for good -
window and tray icon.

## context menu

fill in the fields and druid adds `resize selected images to 800x600` to the
right click menu of every image in explorer and on the desktop. clicking it
resizes the selection into the folder each image already lives in, with the
same naming as above.

the entry mirrors the window: `keep aspect ratio` turns it into
`resize selected images to fit 800x600`, and clearing the fields removes it.
it exists only while druid is running - quitting takes it away, since the
entry needs druid alive to do the work.

it is registered per user under
`HKCU\Software\Classes\SystemFileAssociations`, needs no admin rights, and is
deleted on exit.

## shortcut

    powershell -ExecutionPolicy Bypass -File shortcut.ps1

creates `druid.lnk`, which opens the app with no console window and uses
`icon.ico`. move or copy it anywhere - desktop, start menu, taskbar - it
points at absolute paths. pass a folder to create it there directly:

    powershell -ExecutionPolicy Bypass -File shortcut.ps1 "$env:USERPROFILE\Desktop"

run it again if you move the project or switch python versions. opening druid
a second time just brings the running window to the front.
