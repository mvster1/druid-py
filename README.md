<img src="icon.png" alt="druid" width="128">

## druid

druid is a batch image resizer. all in one file, no configuration necessary.

### dependencies

    pip install "pyvips[binary]" tkinterdnd2

`tkinterdnd2` is optional: without it dragging and dropping images doesn't work, the rest works.

### usage

    python druid.py        # or pythonw druid.py, no console window

1. drop images onto the list or click `select images`
2. fill in `width` and/or `height`
3. `resize` asks where to save

with `keep aspect ratio` the image fits inside the width x height box and
only one of the two is required. without it, both are required and the
image is forced to the exact size.

the output format follows the original file extension. a file that would
overwrite its own original gets a `-WIDTHxHEIGHT` suffix.

## shortcut

    powershell -ExecutionPolicy Bypass -File shortcut.ps1

creates `druid.lnk`, which opens the app with no console window and uses
`icon.ico`. move or copy it anywhere - desktop, start menu, taskbar - it
points at absolute paths. pass a folder to create it there directly:

    powershell -ExecutionPolicy Bypass -File shortcut.ps1 "$env:USERPROFILE\Desktop"

run it again if you move the project or switch python versions.
