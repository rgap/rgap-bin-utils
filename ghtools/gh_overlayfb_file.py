#!/usr/bin/env python3
"""It adds a fb live overlay to an image

Usage:
    rgap_overlayfb_file.py <input> <output> <overlay> [--suffix] [--top0]
    rgap_overlayfb_file.py <input> <overlay> [--suffix] [--top0]

    rgap_overlayfb_file.py -h

Arguments:
    input   input image path
    output  output image path
    overlay overlay image path

Options:
    --suffix    to add a suffixes "_o.png"
    --top0      to cut the image from the top
"""

import math
import os

from PIL import Image


def main(args):
    input_file = args["<input>"]
    output_file = args["<output>"]
    overlay_file = args["<overlay>"]
    suffix = args["--suffix"]
    top0 = args["--top0"]

    # Load image
    img = Image.open(input_file).convert("RGBA")

    if not output_file:
        output_file = input_file
        input_name, input_extension = os.path.splitext(input_file)
        # Add suffix if necessary
        if suffix:
            name_suffix = "_o" + input_extension
            output_file = input_name + name_suffix

    width, height = img.size  # Get dimensions

    overlay = Image.open(overlay_file).convert("RGBA")
    new_width, new_height = overlay.size

    left = math.floor((width - new_width) / 2)
    if top0:
        top = 0
    else:
        top = math.floor((height - new_height) / 2)
    right = left + new_width
    bottom = top + new_height

    img_cropped = img.crop((left, top, right, bottom))
    img_output = Image.alpha_composite(img_cropped, overlay)

    # Save it back to disk
    print(output_file)
    img_output.save(output_file)


if __name__ == "__main__":
    # This will only be executed when this module is run direcly
    from docopt import docopt

    main(docopt(__doc__))
