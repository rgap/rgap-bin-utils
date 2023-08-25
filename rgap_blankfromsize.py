#!/usr/bin/env python3
"""Creates a blank image "_blank.png" with a specified size

Usage:
    rgap_blankfromsize.py <size> [--c <color>]

    rgap_blankfromsize.py -h

Arguments:
    size    width,height (e.g. 128,128)
    color   color (e.g. white, black)

"""

import os
import re

from PIL import Image


def main(args):
    size = args["<size>"]
    color = args["<color>"]

    p = re.compile("(?:^|(?<=,))[^,]*")
    w, h = re.findall(p, size)

    if not color:
        color = "white"
    img = Image.new("RGB", (int(w), int(h)), color=color)

    output_file = w + "_" + h + "_blank.png"
    # Save it back to disk
    img.save(output_file)


if __name__ == "__main__":
    # This will only be executed when this module is run direcly
    from docopt import docopt

    main(docopt(__doc__))
