#!/usr/bin/env python3
"""Trim white or near-white background from images in a directory.

Usage:
    rgap_imagecrop.py (--c|<input_dir>) <output_dir> [--suffix] [--tolerance=<n>]
    rgap_imagecrop.py (--c|<input_dir>) [--suffix] [--tolerance=<n>]
    rgap_imagecrop.py -h

Arguments:
    input_dir   Input directory containing images
    output_dir  Output directory for cropped images

Options:
    --c               Use current directory as input_dir
    --suffix          Add "_cropped" suffix to output filenames
    --tolerance=<n>   Near-white threshold from 0-255 [default: 245]
"""

import os
from PIL import Image


def trim(im, tolerance=200, alpha_tolerance=0):
    """
    Crop all white or near-white background from the outer edges of an image.

    A pixel is considered background if:
    - it is transparent enough, OR
    - all RGB channels are >= tolerance

    This trims from top, bottom, left, and right using the bounding box
    of the remaining content.

    Args:
        im (PIL.Image): Input image.
        tolerance (int): RGB threshold for near-white background.
        alpha_tolerance (int): Alpha threshold for transparency.

    Returns:
        PIL.Image or None: Cropped image, or None if no non-background content exists.
    """
    rgba = im.convert("RGBA")
    pixels = rgba.load()
    width, height = rgba.size

    left = width
    top = height
    right = -1
    bottom = -1

    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]

            is_background = (
                a <= alpha_tolerance or
                (r >= tolerance and g >= tolerance and b >= tolerance)
            )

            if not is_background:
                if x < left:
                    left = x
                if x > right:
                    right = x
                if y < top:
                    top = y
                if y > bottom:
                    bottom = y

    if right == -1 or bottom == -1:
        return None

    return im.crop((left, top, right + 1, bottom + 1))


def main(args):
    input_dir = args["<input_dir>"]
    output_dir = args["<output_dir>"]
    current_directory = args["--c"]
    suffix = args["--suffix"]
    tolerance = int(args["--tolerance"])

    if current_directory:
        input_dir = os.getcwd()

    if not output_dir:
        output_dir = input_dir

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"input_dir = {input_dir}\noutput_dir = {output_dir}\n")
    print(f"tolerance = {tolerance}\n")

    extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}

    for entry in os.listdir(input_dir):
        input_file = os.path.join(input_dir, entry)

        if not os.path.isfile(input_file):
            continue

        input_name, input_extension = os.path.splitext(entry)

        if input_extension.lower() not in extensions:
            continue

        output_filename = entry

        if suffix:
            name_suffix = "_cropped" + input_extension
            if entry.endswith(name_suffix):
                continue
            output_filename = input_name + name_suffix

        output_file = os.path.join(output_dir, output_filename)

        try:
            img = Image.open(input_file)
            trimmed_img = trim(img, tolerance=tolerance)

            if trimmed_img:
                trimmed_img.save(output_file)
                print(f"Saved: {output_file}")
            else:
                print(f"Skipped (image is fully white/empty): {input_file}")

        except Exception as e:
            print(f"Error processing {input_file}: {e}")


if __name__ == "__main__":
    from docopt import docopt
    main(docopt(__doc__))