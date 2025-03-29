#!/usr/bin/env python3
"""Convert non-JPG images in a directory to JPG

Usage:
    rgap_image_convert_to_jpg.py (--c|<input_dir>) <output_dir> [--suffix] [--quality=<quality>]
    rgap_image_convert_to_jpg.py (--c|<input_dir>) [--suffix] [--quality=<quality>]

    rgap_image_convert_to_jpg.py -h

Arguments:
    input_dir           input directory containing images
    output_dir          output directory to save converted JPG images
    --c                 to make input_dir the current directory

Options:
    --suffix            to add a suffix "_converted" to output filename
    --quality=<quality> quality percentage for output JPG images (1-100, default is 80)

"""

import os
from PIL import Image

def convert_to_jpg(im, output_file, quality=80):
    """Convert an image to JPG format."""
    # Ensure the image is in RGB mode (necessary for JPG)
    if im.mode != "RGB":
        im = im.convert("RGB")
    im.save(output_file, "JPEG", quality=quality)

def main(args):
    input_dir = args["<input_dir>"]
    output_dir = args.get("<output_dir>")
    current_directory = args["--c"]
    suffix = args["--suffix"]
    quality = args["--quality"]

    # Use the current directory if specified
    if current_directory:
        input_dir = os.getcwd()

    if not output_dir:
        output_dir = input_dir

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Set default quality if not provided
    quality = int(quality) if quality else 80

    print(
        ("input_dir = %s\noutput_dir = %s\nquality = %d\n") %
        (input_dir, output_dir, quality)
    )

    for input_filename in os.listdir(input_dir):
        # Skip files that already have a .jpg extension
        if input_filename.lower().endswith(".jpg"):
            continue

        input_file = os.path.join(input_dir, input_filename)
        input_name, input_extension = os.path.splitext(input_filename)

        # Build the output filename; add suffix if necessary
        if suffix:
            output_filename = input_name + "_converted.jpg"
        else:
            output_filename = input_name + ".jpg"
        output_file = os.path.join(output_dir, output_filename)

        try:
            with Image.open(input_file) as img:
                convert_to_jpg(img, output_file, quality=quality)
                print("Converted:", output_file)
        except Exception as e:
            print("Skipping {}: {}".format(input_file, e))

if __name__ == "__main__":
    from docopt import docopt
    main(docopt(__doc__))
