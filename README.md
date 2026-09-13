<img src="icon.png" alt="druid" width="128">

## druid

druid is a batch image resizer. all in one file, no configuration necessary.

### dependencies

    pip install "pyvips[binary]" tkinterdnd2 pystray

`tkinterdnd2` is optional: without it dragging and dropping images doesn't work, the rest works.

### usage

    python druid.py        # or pythonw druid.py, no console window

1. drag and drop images onto the list or click `select images` to add them
2. fill in `width` and/or `height`
3. click `resize` for it to ask where to save the resized images

with `keep aspect ratio` the image fits inside the width x height box and
only one of the two is required. without this option checked, both width and height are required and the
image is forced to the exact typed values.

the output format follows the original file extension, and every file gets a `RESIZED___` prefix and a
`___WIDTHxHEIGHT` suffix, identifying the file had been resized and naming the size it came out as - so nothing
overwrites the originals.

while druid runs, its icon sits in the tray and clicking it brings the window
back. minimizing behaves like any other app; it is not hidden for better control. 
closing the window quits druid for good, killing it completely.

## context menu

filling in the fields in the app, druid adds `resize selected images to WIDTHxHEIGHT` to the
right click context menu of every image in explorer (including the desktop). clicking it
resizes the selected images to the dimensions typed in the app and saves the resized images in
the folder each image already lives in, with the same naming pattern described above.

this context menu entry mirrors the window: `keep aspect ratio` turns it into
`resize selected images to fit WIDTHxHEIGHT`, and clearing the w/h fields removes that entry.
it exists only while druid is running - quitting takes it away, since the
entry needs druid alive to exist.

it is registered per user under
`HKCU\Software\Classes\SystemFileAssociations`, needs no admin rights, and is
automatically deleted on exit.

## shortcut (optional)

    powershell -ExecutionPolicy Bypass -File shortcut.ps1

creates `druid.lnk`, which opens the app with no console window and uses
`icon.ico`. move or copy it anywhere and it should work since it
points at absolute paths. pass a folder to create it there directly:

    powershell -ExecutionPolicy Bypass -File shortcut.ps1 "$env:USERPROFILE\Desktop"

run it again if you move the project or switch python versions. opening druid
a second time just brings the running window to the front.

## credits
the logo image was made by Hellraiser140[https://www.reddit.com/user/Hellraiser140/] on reddit[https://www.reddit.com/r/PixelArt/comments/cm5or7/oc_i_made_a_little_druid_sprite_for_my_first_ever/]