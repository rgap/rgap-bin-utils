#!/usr/bin/env python3
"""Reduce quality of a single image file

Usage:
    rgap_image_reducequality_dir.py <input> <output> [--quality=<quality>] [--compress_level=<compress_level>] [--suffix]
    rgap_image_reducequality_dir.py <input> [--quality=<quality>] [--compress_level=<compress_level>] [--suffix]

    rgap_image_reducequality_dir.py -h

Arguments:
    input               input image file path
    output              output image file path

Options:
    --quality=<quality>         quality percentage for output JPG images (1-100, default is 50)
    --compress_level=<compress_level> compression level for PNG images (1-9, default is 6)
    --suffix                    to add a suffix "_reduced"

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
    input_file = args["<input>"]
    output_file = args["<output>"]
    quality = args["--quality"]
    compress_level = args["--compress_level"]
    suffix = args["--suffix"]

    # Set default quality and compress level if not provided
    quality = int(quality) if quality else 50
    compress_level = int(compress_level) if compress_level else 6

    # Determine output file path
    if not output_file:
        output_file = input_file
        input_name, input_extension = os.path.splitext(input_file)
        # Add suffix if necessary
        if suffix:
            name_suffix = "_reduced" + input_extension
            output_file = input_name + name_suffix

    # Load and process image
    img = Image.open(input_file)

    if input_file.lower().endswith(".jpg"):
        reduce_quality(img, output_file, quality=quality)
        print(f"Processed JPG: {output_file}")
    elif input_file.lower().endswith(".png"):
        optimize_png(img, output_file, compress_level=compress_level)
        print(f"Processed PNG: {output_file}")
    else:
        print("Unsupported file type. Only JPG and PNG are supported.")

if __name__ == "__main__":
    # This will only be executed when this module is run directly
    from docopt import docopt

    main(docopt(__doc__))
