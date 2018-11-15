#!/usr/bin/env python3
"""It renames images from "Best Link 2018.png" to "best-link-2018.png"

Usage:
    rgap_renamefiles.py (--c|<input_dir>)

    rgap_renamefiles.py -h

Arguments:
    input_dir   input directory path

Options:
    --c     current directory
"""

import os
import re

def main(args):

    input_dir = args['<input_dir>']
    current_directory = args['--c']

    # In case the current directory is the one used
    if current_directory:
        input_dir = os.getcwd()

    output_dir = input_dir
    # If the output directory doesn't exist then create it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for input_filename in os.listdir(input_dir):
        output_filename = input_filename
        input_name, input_extension = os.path.splitext(input_filename)

        output_filename = input_name.strip().lower().replace('_', ' ').replace('-', ' ')
        output_filename = re.sub(' +', ' ', output_filename)
        output_filename = output_filename.replace(' ', '-') + input_extension

        extensions = [".jpg", ".png", ".gif", ".tif"]
        is_an_image = any(input_filename.lower().endswith(e)
                          for e in extensions)
        if is_an_image:
            input_file = os.path.join(input_dir, input_filename)
            output_file = os.path.join(output_dir, output_filename)
            os.rename(input_file, output_file)
            print(output_file)


if __name__ == "__main__":
    # This will only be executed when this module is run direcly
    from docopt import docopt
    main(docopt(__doc__))
