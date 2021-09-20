#!/usr/bin/env python3
""" TXT FILE TO PDF

Usage:
    rgap_txt2pdf_dir.py (--c|<input_dir>) <output_dir> [--suffix]
    rgap_txt2pdf_dir.py (--c|<input_dir>) [--suffix]

    rgap_txt2pdf_dir.py -h

Arguments:
    input_dir   input directory containing images
    output_dir  output directory containing images
    --c         to make input_dir the current directory

Options:
    --suffix                                 to add a suffixes "_conv.txt"

"""

import os


def main(args):

    input_dir = args['<input_dir>']
    output_dir = args['<output_dir>']
    current_directory = args['--c']
    suffix = args['--suffix']

    # In case the current directory is the one used
    if current_directory:
        input_dir = os.getcwd()

    if not output_dir:
        output_dir = input_dir
    # If the output directory doesn't exist then create it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(("input_dir = %s\noutput_dir = %s\n") % (input_dir, output_dir))

    for input_filename in os.listdir(input_dir):
        output_filename = input_filename

        name_suffix = ".pdf"
        # Add suffix if necessary
        if suffix:
            name_suffix = "_conv.pdf"
            if name_suffix in input_filename:
                continue
        output_filename = (os.path.splitext(input_filename)[0] +
                           name_suffix)

        # Check if it's a txt
        is_image = input_filename.lower().endswith(".txt")
        if is_image:
            input_file = os.path.join(input_dir, input_filename)
            output_file = os.path.join(output_dir, output_filename)

            command = (('pandoc -V geometry:paperwidth=4in -V geometry:paperheight=6in -V geometry:margin=.5in "%s" -o "%s"') %
                       (input_file, output_file))

            # Run command
            try:
                os.system(command)
            except:
                print("error on convert")
                raise
            print(output_file)
        else:
            continue

if __name__ == "__main__":
    # This will only be executed when this module is run direcly
    from docopt import docopt
    main(docopt(__doc__))
