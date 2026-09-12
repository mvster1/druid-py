<img src="icon.png" alt="druid" width="128">

# druid

batch image resizer. one file, no configuration.

## dependencies

    pip install "pyvips[binary]" tkinterdnd2

`tkinterdnd2` is optional: without it drag and drop is gone, the rest works.

## usage

    python druid.py        # or pythonw druid.py, no console window

1. drop images onto the list or click `select images`
2. fill in `width` and/or `height`
3. `resize` asks where to save

with `keep aspect ratio` the image fits inside the width x height box and
only one of the two is required. without it, both are required and the
image is forced to the exact size.

the output format follows the original file extension. a file that would
overwrite its own original gets a `-WIDTHxHEIGHT` suffix.
