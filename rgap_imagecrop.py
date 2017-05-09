#!/usr/bin/env python3
"""Trim whitespace from images in a directory

Usage:
    rgap_imagecrop.py (--c|<input_dir>) <output_dir> [--suffix]
    rgap_imagecrop.py (--c|<input_dir>) [--suffix]

    rgap_imagecrop.py -h

Arguments:
    input_dir   input directory containing images
    output_dir  output directory containing images
    --c         to make input_dir the current directory

Options:
    --suffix    to add a suffixes "_cropped.pdf"

"""

import os
from PIL import Image, ImageChops


def trim(im):
    bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, 0)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)


def main(args):

    input_dir = args['<input_dir>']
    output_dir = args['<output_dir>']
    current_directory = args['--c']
    suffix = args['--suffix']

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
            name_suffix = "_cropped" + input_extension
            if name_suffix in input_filename:
                continue
            output_filename = (input_name + name_suffix)

        # Check if it's an image
        extensions = [".jpg", ".png", ".gif"]
        is_an_image = any(input_filename.lower().endswith(e)
                          for e in extensions)
        if is_an_image:
            input_file = os.path.join(input_dir, input_filename)
            output_file = os.path.join(output_dir, output_filename)

            # Load and trim image
            img = Image.open(input_file)
            img = trim(img)

            # Save it back to disk
            img.save(output_file)
            print(output_file)

if __name__ == "__main__":
    # This will only be executed when this module is run direcly
    from docopt import docopt
    main(docopt(__doc__))
