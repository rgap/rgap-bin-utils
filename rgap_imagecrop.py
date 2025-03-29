#!/usr/bin/env python3
"""Trim whitespace (including white or near-white backgrounds) from images in a directory

Usage:
    rgap_imagecrop.py (--c|<input_dir>) <output_dir> [--suffix]
    rgap_imagecrop.py (--c|<input_dir>) [--suffix]

    rgap_imagecrop.py -h

Arguments:
    input_dir   input directory containing images
    output_dir  output directory containing images
    --c         to make input_dir the current directory

Options:
    --suffix    to add a suffix "_cropped" to output filenames.

"""

import os
from PIL import Image, ImageChops


def trim(im, tolerance=245):
    """
    Trims white or near-white backgrounds from the image.

    Args:
        im (PIL.Image): The input image.
        tolerance (int): Brightness level to consider as "background" (0-255).

    Returns:
        PIL.Image or None: Cropped image or None if no content to crop.
    """
    # Convert image to grayscale for easier processing
    grayscale = im.convert("L")

    # Create a binary mask where white areas are treated as "background"
    binary_mask = grayscale.point(lambda x: 0 if x > tolerance else 255, mode="1")

    # Get the bounding box of the non-background content
    bbox = binary_mask.getbbox()

    if bbox:
        return im.crop(bbox)
    return None


def main(args):
    input_dir = args["<input_dir>"]
    output_dir = args["<output_dir>"]
    current_directory = args["--c"]
    suffix = args["--suffix"]

    # Use the current directory if specified
    if current_directory:
        input_dir = os.getcwd()

    if not output_dir:
        output_dir = input_dir
    # Create the output directory if it doesn't exist
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
            output_filename = input_name + name_suffix

        # Check if it's an image
        extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"]
        is_an_image = any(input_filename.lower().endswith(e) for e in extensions)
        if is_an_image:
            input_file = os.path.join(input_dir, input_filename)
            output_file = os.path.join(output_dir, output_filename)

            # Load and trim image
            img = Image.open(input_file)
            trimmed_img = trim(img)

            # Save trimmed image if it exists
            if trimmed_img:
                trimmed_img.save(output_file)
                print(f"Saved: {output_file}")
            else:
                print(f"Skipped (no content to crop): {input_file}")


if __name__ == "__main__":
    # This will only be executed when this module is run directly
    from docopt import docopt

    main(docopt(__doc__))
