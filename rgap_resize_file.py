#!/usr/bin/env python
"""Image file resizer

Usage:
    rgap_resizefile.py <input> <output> <width> <height>
    rgap_resizefile.py <input> <width> <height>
    rgap_resizefile.py <input> <output> -w <width>
    rgap_resizefile.py <input> -w <width>
    rgap_resizefile.py <input> <output> -h <height>
    rgap_resizefile.py <input> -h <height>
    rgap_resizefile.py -h

Arguments:
    input   input image path
    output  output image path
    width   new image width
    height  new image height

"""

from PIL import Image


def main(args):

    input_file = args['<input>']
    output_file = args['<output>']
    w = args['<width>']
    h = args['<height>']

    # Load image
    img = Image.open(input_file)

    if not output_file:
        output_file = input_file
    if w and h:
        h = int(h)
        w = int(w)
    if not w:
        h = int(h)
        w = int(h * img.width / img.height)
    if not h:
        w = int(w)
        h = int(w * img.height / img.width)

    # Resize it
    img = img.resize((w, h), Image.BILINEAR)

    # Save it back to disk
    img.save(output_file)

if __name__ == "__main__":
    # This will only be executed when this module is run direcly
    from docopt import docopt
    main(docopt(__doc__))
