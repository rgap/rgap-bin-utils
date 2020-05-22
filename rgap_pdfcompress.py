#!/usr/bin/env python3
"""PDF Compression
It uses https://blog.omgmog.net/post/compressing-pdf-from-your-mac-or-linux-terminal-with-ghostscript/

Usage:
    rgap_pdfcompress.py (--c|<input_dir>) <output_dir> [--suffix]
    rgap_pdfcompress.py (--c|<input_dir>) [--suffix]

    rgap_pdfcompress.py -h

Arguments:
    input_dir   input directory containing pdf files
    output_dir  output directory containing pdf files
    --c         to make input_dir the current directory

Options:
    --suffix                                 to add a suffixes "_compressed.pdf"

Examples:
    rgap_pdfcompress.py --c

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

        # Add suffix if necessary
        if suffix:
            name_suffix = "_compressed.pdf"
            if name_suffix in input_filename:
                continue
            output_filename = (os.path.splitext(input_filename)[0] +
                               name_suffix)

        # Check if it's a pdf
        is_a_pdf = input_filename.lower().endswith(".pdf")
        if is_a_pdf:
            input_file = os.path.join(input_dir, input_filename)
            output_file = os.path.join(output_dir, output_filename)
            tmp_file = os.path.join(input_dir, os.path.splitext(input_filename)[0] + '_#00tmp.pdf')
            os.system("cp {} {}".format(input_file, tmp_file))

            command = "gs -sDEVICE=pdfwrite -dNOPAUSE -dQUIET -dBATCH -dPDFSETTINGS=/screen -dCompatibilityLevel=1.4 -sOutputFile={} {}".format(output_file, tmp_file)
            print(command)
            # Run pdfcrop command
            try:
                os.system(command)
            except:
                print("error on compresspdf")
                raise
            # print(output_file)
            os.system("rm {}".format(tmp_file))
        else:
            continue

if __name__ == "__main__":
    # This will only be executed when this module is run direcly
    from docopt import docopt
    main(docopt(__doc__))
