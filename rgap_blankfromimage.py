#!/usr/bin/env python3
"""Creates a blank image "_blank.png" with the size of the input one

Usage:
    rgap_blankfromimage.py <input> <output> [--c <color>]
    rgap_blankfromimage.py <input> [--c <color>]

    rgap_blankfromimage.py -h

Arguments:
    input   input image path
    output  output image path
    color   color (e.g. white, black)

"""

import os

from PIL import Image


def main(args):
    input_file = args["<input>"]
    output_file = args["<output>"]
    color = args["<color>"]

    # Load image
    img = Image.open(input_file)

    if not output_file:
        output_file = input_file
        input_name, input_extension = os.path.splitext(input_file)
        name_suffix = "_blank" + input_extension
        output_file = input_name + name_suffix

    if not color:
        color = "white"
    img = Image.new("RGB", (img.width, img.height), color=color)

    # Save it back to disk
    img.save(output_file)


if __name__ == "__main__":
    # This will only be executed when this module is run direcly
    from docopt import docopt

    main(docopt(__doc__))
