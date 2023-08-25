#!/usr/bin/env python3
"""Convert image to grayscale

Usage:
    rgap_imagegray.py <input> <output> [--suffix]
    rgap_imagegray.py <input> [--suffix]

    rgap_imagegray.py -h

Arguments:
    input   input image path
    output  output image path

Options:
    --suffix    to add a suffixes "_conv.png"
"""

import os

from PIL import Image


def main(args):
    input_file = args["<input>"]
    output_file = args["<output>"]
    suffix = args["--suffix"]

    # Load image
    img = Image.open(input_file)

    if not output_file:
        output_file = input_file
        input_name, input_extension = os.path.splitext(input_file)
        # Add suffix if necessary
        if suffix:
            name_suffix = "_conv" + input_extension
            output_file = input_name + name_suffix

    # Resize it
    img = img.convert("L")

    # Save it back to disk
    img.save(output_file)


if __name__ == "__main__":
    # This will only be executed when this module is run direcly
    from docopt import docopt

    main(docopt(__doc__))
