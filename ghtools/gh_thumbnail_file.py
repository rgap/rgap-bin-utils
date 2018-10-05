#!/usr/bin/env python3
"""This will scale the input image to the specified height, but the output
will have the whole size

Usage:
    py <input> <output> <width> <height>
    py <input> <width> <height> [--nosuffix]

    py -h

Arguments:
    input   input image path
    output  output image path
    width   output image width
    height  output image height

Options:
    --nosuffix    to not add a suffix "_o.png"
"""

from PIL import Image, ImageFilter
import math
import sys
import os


# img = Image.open("bg/background.png")

def gh_resize(input_file, w=None, h=None):

    # Load image
    img = Image.open(input_file).convert("RGBA")

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
    output = img.resize((w_new, h_new), Image.BOX).convert("RGBA")
    return output


def main(args):
    input_file = args['<input>']
    output_file = args['<output>']
    w = args['<width>']
    h = args['<height>']
    nosuffix = args['--nosuffix']

    if not output_file:
        output_file = input_file
        input_name, input_extension = os.path.splitext(input_file)
        # Add suffix if necessary
        if not nosuffix:
            name_suffix = "_o" + input_extension
            output_file = (input_name + name_suffix)

    resized = gh_resize(input_file, h=h)

    transp_img = Image.new('RGBA', (int(w), int(h)), (0, 0, 0, 0))

    output = transp_img.copy()
    position = (math.floor((transp_img.width - resized.width)/2), math.floor((transp_img.height - resized.height)/2))
    output.paste(resized, position)

    # output = Image.alpha_composite(transp_img, resized)
    output.save(output_file, "PNG")


if __name__ == "__main__":
    # This will only be executed when this module is run direcly
    from docopt import docopt
    main(docopt(__doc__))
