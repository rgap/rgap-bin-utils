#!/usr/bin/env python3
"""This will scale the input directory images to the specified height, but the
output will have the whole size

Usage:
    gh_thumbnail_dir.py (--c|<input_dir>) <output_dir> <width> <height>
    gh_thumbnail_dir.py (--c|<input_dir>) <width> <height> [--nosuffix]

    gh_thumbnail_dir.py -h

Arguments:
    input_dir   input directory containing images
    output_dir  output directory containing images
    width   output image width
    height  output image height

Options:
    --c         to make input_dir the current directory
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

    input_dir = args['<input_dir>']
    output_dir = args['<output_dir>']
    w = args['<width>']
    h = args['<height>']
    current_directory = args['--c']
    nosuffix = args['--nosuffix']

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
        if not nosuffix:
            name_suffix = "_o" + input_extension
            if name_suffix in input_filename:
                continue
            output_filename = (input_name + name_suffix)

        extensions = [".jpg", ".png", ".gif", ".tif"]
        is_an_image = any(input_filename.lower().endswith(e)
                          for e in extensions)
        if is_an_image:
            input_file = os.path.join(input_dir, input_filename)
            output_file = os.path.join(output_dir, output_filename)

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
