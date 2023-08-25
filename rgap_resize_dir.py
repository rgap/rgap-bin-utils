#!/usr/bin/env python3
"""Resize images from a directory

Usage:
    rgap_resize_dir.py (--c|<input_dir>) <output_dir> <width> <height> [--suffix]
    rgap_resize_dir.py (--c|<input_dir>) <width> <height> [--suffix]
    rgap_resize_dir.py (--c|<input_dir>) <output_dir> --w <width> [--suffix]
    rgap_resize_dir.py (--c|<input_dir>) --w <width> [--suffix]
    rgap_resize_dir.py (--c|<input_dir>) <output_dir> --h <height> [--suffix]
    rgap_resize_dir.py (--c|<input_dir>) --h <height> [--suffix]

    rgap_resize_dir.py -h

Arguments:
    input_dir   input directory containing images
    output_dir  output directory containing images
    width       width for the new images
    height      height for the new images
    --c         to make input_dir the current directory

Options:
    --suffix    to add a suffixes "_resized.png"
"""

import os

from PIL import Image


def main(args):
    input_dir = args["<input_dir>"]
    output_dir = args["<output_dir>"]
    w = args["<width>"]
    h = args["<height>"]
    current_directory = args["--c"]
    suffix = args["--suffix"]

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
            name_suffix = "_resized" + input_extension
            if name_suffix in input_filename:
                continue
            output_filename = input_name + name_suffix

        extensions = [".jpg", ".jpeg", ".png", ".gif", ".tif"]
        is_an_image = any(input_filename.lower().endswith(e) for e in extensions)
        if is_an_image:
            input_file = os.path.join(input_dir, input_filename)
            output_file = os.path.join(output_dir, output_filename)

            # Load image
            img = Image.open(input_file)

            if w and h:
                h_new = int(h)
                w_new = int(w)
            elif not w:
                h_new = int(h)
                w_new = int(h_new * img.width / img.height)
            elif not h:
                w_new = int(w)
                h_new = int(w_new * img.height / img.width)

            # Resize it
            img = img.resize((w_new, h_new), Image.BILINEAR)

            # Save it back to disk
            img.save(output_file)
            print(output_file)


if __name__ == "__main__":
    # This will only be executed when this module is run direcly
    from docopt import docopt

    main(docopt(__doc__))
