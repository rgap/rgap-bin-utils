#!/usr/bin/env python3
"""It adds a fb live overlay to images from a directory

Usage:
    rgap_overlayfb_dir.py (--c|<input_dir>) <output_dir> <overlay> [--suffix] [--top0]
    rgap_overlayfb_dir.py (--c|<input_dir>) <overlay> [--suffix] [--top0]

    rgap_overlayfb_dir.py -h

Arguments:
    input_dir   input directory containing images
    output_dir  output directory containing images
    overlay     overlay image path
    --c         to make input_dir the current directory
    --suffix    to add a suffixes "_o.png"
    --top0      to cut the image from the top

"""

import math
import os

from PIL import Image


def main(args):
    input_dir = args["<input_dir>"]
    output_dir = args["<output_dir>"]
    overlay_file = args["<overlay>"]
    current_directory = args["--c"]
    suffix = args["--suffix"]
    top0 = args["--top0"]

    # In case the current directory is the one used
    if current_directory:
        input_dir = os.getcwd()

    if not output_dir:
        output_dir = input_dir
    # If the output directory doesn't exist then create it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(("input_dir = %s\noutput_dir = %s\n") % (input_dir, output_dir))

    for input_filename in os.listdir(input_dir):
        output_filename = input_filename
        input_name, input_extension = os.path.splitext(input_filename)
        # Add suffix if necessary
        if suffix:
            name_suffix = "_o" + input_extension
            if name_suffix in input_filename:
                continue
            output_filename = input_name + name_suffix

        extensions = [".jpg", ".png", ".gif", ".tif"]
        is_an_image = any(input_filename.lower().endswith(e) for e in extensions)
        if is_an_image:
            input_file = os.path.join(input_dir, input_filename)
            output_file = os.path.join(output_dir, output_filename)

            # Load image
            img = Image.open(input_file).convert("RGBA")

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
            img_output.save(output_file)
            print(output_file)


if __name__ == "__main__":
    # This will only be executed when this module is run direcly
    from docopt import docopt

    main(docopt(__doc__))
