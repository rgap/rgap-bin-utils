#!/usr/bin/env python3
"""Image rotation

Usage:
    rgap_rotate_file.py <input> <output> <angle>
    rgap_rotate_file.py <input> <angle>
    
    rgap_rotate_file.py -h

Arguments:
    input   input image path
    output  output image path
    angle   clockwise rotation angle

"""

from PIL import Image


def main(args):
    input_file = args["<input>"]
    output_file = args["<output>"]
    angle = int(args["<angle>"])

    # Load image
    img = Image.open(input_file)

    if not output_file:
        output_file = input_file

    # Rotation
    img = img.rotate(angle, expand=1)

    # Save it back to disk
    img.save(output_file)


if __name__ == "__main__":
    # This will only be executed when this module is run direcly
    from docopt import docopt

    main(docopt(__doc__))
