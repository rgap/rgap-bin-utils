#!/usr/bin/env python3
"""Crops margins of PDFs in a directory

This script makes use of "ImageMagick" library
http://www.imagemagick.org/script/index.php
On Mac OS X: brew install imagemagick

Uses to "pdfcrop" single pdf files

It allows cropping the margins of PDF files in a specific
directoty, very useful specially when having a bunch of files
that have a blank margin and a diagram in the center.

Usage:
    rgap_pdfcrop.py (--c|<input_dir>) <output_dir> [--suffix] [--margins="<margins>"]
    rgap_pdfcrop.py (--c|<input_dir>) [--suffix] [--margins="<margins>"]

    rgap_pdfcrop.py -h

Arguments:
    input_dir   input directory containing pdf files
    output_dir  output directory containing pdf files
    --c         to make input_dir the current directory

Options:
    --suffix                                 to add a suffixes "_cropped.pdf"
    --margin="<left> <top> <right> <bottom>" adds extra margins, unit is bp.
                                             If only one number is given, then
                                             it is used for all  margins, in
                                             the case of two numbers they are
                                             also used for right and bottom.

"""

import os


def main(args):

    input_dir = args['<input_dir>']
    output_dir = args['<output_dir>']
    margins = args['--margins']
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

        # Add suffix if necessary
        if suffix:
            name_suffix = "_cropped.pdf"
            if name_suffix in input_filename:
                continue
            output_filename = (os.path.splitext(input_filename)[0] +
                               name_suffix)

        # Check if it's a pdf
        is_a_pdf = input_filename.lower().endswith(".pdf")
        if is_a_pdf:
            input_file = os.path.join(input_dir, input_filename)
            output_file = os.path.join(output_dir, output_filename)

            command = ("pdfcrop %s %s ") % (input_file, output_file)
            if margins is not None:
                command += (" --margins '%s'") % (margins)

            # Run pdfcrop command
            try:
                os.system(command)
            except:
                print("error on pdfcrop")
                raise
            # print(output_file)
        else:
            continue

if __name__ == "__main__":
    # This will only be executed when this module is run direcly
    from docopt import docopt
    main(docopt(__doc__))
