#!/usr/bin/env python3
"""Creates a blank circle "_circle.png" with a specified size

Usage:
    rgap_blankcircle.py <size> [--c <color>] [--cross]

    rgap_blankcircle.py -h

Arguments:
    size    width,height (e.g. 128,128)
    color   color (e.g. white, black)
    cross    to draw a cross of the inverted color in the center of the circle
"""

import os
import re

import webcolors
from PIL import Image, ImageDraw


def main(args):
    size = args["<size>"]
    color = args["<color>"]
    cross = args["--cross"]

    p = re.compile("(?:^|(?<=,))[^,]*")
    w_str, h_str = re.findall(p, size)
    w, h = int(w_str), int(h_str)

    if not color:
        color = "black"
    img = Image.new("RGBA", (w - 1, h - 1))
    draw = ImageDraw.Draw(img)
    draw.ellipse((0, 0, w - 2, h - 2), fill=color)

    if cross:
        linecolor = webcolors.name_to_rgb(color)
        linecolor = (255 - linecolor[0], 255 - linecolor[1], 255 - linecolor[2])
        horizontal = ((0 + int(w / 20), h / 2 - 1), (w - int(w / 20) - 2, h / 2 - 1))
        vertical = ((w / 2 - 1, 0 + int(h / 20)), (w / 2 - 1, h - int(h / 20) - 2))
        draw.line(horizontal, fill=linecolor, width=int(h / 20))
        draw.line(vertical, fill=linecolor, width=int(w / 20))
    output_file = w_str + "_" + h_str + "_circle.png"

    # To fix the extra pixels
    img = img.resize((w, h), resample=Image.NEAREST)
    # Save it to disk
    img.save(output_file)


if __name__ == "__main__":
    # This will only be executed when this module is run direcly
    from docopt import docopt

    main(docopt(__doc__))
