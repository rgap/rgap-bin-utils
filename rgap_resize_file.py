#!/usr/bin/env python3
"""Image file resizer

Usage:
    rgap_resize_file.py <input> <output> <width> <height> [--suffix]
    rgap_resize_file.py <input> <width> <height> [--suffix]
    rgap_resize_file.py <input> <output> --w <width> [--suffix]
    rgap_resize_file.py <input> --w <width> [--suffix]
    rgap_resize_file.py <input> <output> --h <height> [--suffix]
    rgap_resize_file.py <input> --h <height> [--suffix]

    rgap_resize_file.py -h

Arguments:
    input   input image path
    output  output image path
    width   new image width
    height  new image height

Options:
    --suffix    to add a suffixes "_resized.png"
"""

import os
from PIL import Image


def main(args):

    input_file = args['<input>']
    output_file = args['<output>']
    w = args['<width>']
    h = args['<height>']
    suffix = args['--suffix']

    # Load image
    img = Image.open(input_file)

    if not output_file:
        output_file = input_file
        input_name, input_extension = os.path.splitext(input_file)
        # Add suffix if necessary
        if suffix:
            name_suffix = "_resized" + input_extension
            output_file = (input_name + name_suffix)

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
    img = img.resize((w_new, h_new), Image.BILINEAR)

    # Save it back to disk
    img.save(output_file)

if __name__ == "__main__":
    # This will only be executed when this module is run direcly
    from docopt import docopt
    main(docopt(__doc__))
