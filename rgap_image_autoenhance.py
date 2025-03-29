#!/usr/bin/env python3
"""Enhanced image artifact remover using ImageMagick
Usage:
    rgap_image_autoenhance.py <input> <output> [--suffix]
    rgap_image_autoenhance.py <input> [--suffix]
"""
import os
import subprocess
from docopt import docopt

def main(args):
    input_file = args["<input>"]
    output_file = args["<output>"]
    suffix = args["--suffix"]
    
    if not output_file:
        input_name, input_extension = os.path.splitext(input_file)
        if suffix:
            output_file = input_name + "_enhanced" + input_extension
        else:
            output_file = input_file
    
    # Use ImageMagick for high-quality enhancement
    cmd = [
        "convert", input_file,
        "-adaptive-blur", "0x1",
        "-unsharp", "0x1",
        "-enhance",
        "-normalize",
        output_file
    ]
    
    print(f"Enhancing image: {input_file}")
    subprocess.run(cmd)
    print(f"Enhanced image saved as: {output_file}")

if __name__ == "__main__":
    main(docopt(__doc__))