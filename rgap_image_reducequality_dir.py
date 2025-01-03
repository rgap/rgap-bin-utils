#!/usr/bin/env python3
"""Reduce quality of JPG images in a directory

Usage:
    rgap_image_reducequality_file.py (--c|<input_dir>) <output_dir> [--suffix] [--quality=<quality>] [--compress_level=<compress_level>]
    rgap_image_reducequality_file.py (--c|<input_dir>) [--suffix] [--quality=<quality>] [--compress_level=<compress_level>]

    rgap_image_reducequality_file.py -h

Arguments:
    input_dir           input directory containing images
    output_dir          output directory containing images
    --c                 to make input_dir the current directory

Options:
    --suffix            to add a suffix "_reduced"
    --quality=<quality> quality percentage for output JPG images (1-100, default is 50)
    --compress_level=<compress_level> compression level for PNG images (1-9, default is 6)

"""

import os

from PIL import Image


def reduce_quality(im, output_file, quality=50):
    """Reduce the quality of a JPG image."""
    im.save(output_file, "JPEG", quality=quality)


def optimize_png(im, output_file, compress_level=6):
    """Optimize a PNG image by adjusting compression level."""
    im.save(output_file, "PNG", compress_level=compress_level)


def main(args):
    input_dir = args["<input_dir>"]
    output_dir = args["<output_dir>"]
    current_directory = args["--c"]
    suffix = args["--suffix"]
    quality = args["--quality"]
    compress_level = args["--compress_level"]

    # Use current directory if specified
    if current_directory:
        input_dir = os.getcwd()

    if not output_dir:
        output_dir = input_dir

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Set default quality and compress level if not provided
    quality = int(quality) if quality else 50
    compress_level = int(compress_level) if compress_level else 6

    print(
        ("input_dir = %s\noutput_dir = %s\nquality = %d\ncompress_level = %d\n") %
        (input_dir, output_dir, quality, compress_level))

    for input_filename in os.listdir(input_dir):
        output_filename = input_filename

        input_name, input_extension = os.path.splitext(input_filename)
        # Add suffix if necessary
        if suffix:
            name_suffix = "_reduced" + input_extension
            if name_suffix in input_filename:
                continue
            output_filename = input_name + name_suffix

        # Process JPG and PNG images
        input_file = os.path.join(input_dir, input_filename)
        output_file = os.path.join(output_dir, output_filename)

        if input_filename.lower().endswith(".jpg"):
            # Load image and reduce quality for JPG
            img = Image.open(input_file)
            reduce_quality(img, output_file, quality=quality)
            print(output_file)
        elif input_filename.lower().endswith(".png"):
            # Load image and optimize PNG
            img = Image.open(input_file)
            optimize_png(img, output_file, compress_level=compress_level)
            print(output_file)


if __name__ == "__main__":
    # This will only be executed when this module is run directly
    from docopt import docopt

    main(docopt(__doc__))
