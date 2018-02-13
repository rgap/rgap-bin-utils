#!/usr/bin/env python3
"""Run a script with its arguments using the files from the current directory

Usage:
    rgap_runargs_dir.py <script> <arguments> [--images] [--prefix=<prefix>] [--test]

    rgap_runargs_dir.py -h

Arguments:
    script          script to run
    arguments       arguments

Options:
    --test          for testing this command

Examples:
    rgap_runargs_dir.py convert "<input_filename> -crop <img.width>x<img.height>-0-15 <output_filename>" --image --prefix=conv

"""

import os
import re
from PIL import Image, ImageChops


def main(args):
    script = args['<script>']
    arguments = args['<arguments>']
    images = args['--images']
    prefix = args['--prefix']
    test = args['--test']

    # In case the current directory is the one used
    input_dir = os.getcwd()

    arguments = arguments.split(' ')
    index_params = []
    argument_list = []
    for i in range(len(arguments)):
        params = re.findall(r'<(.+?)>', arguments[i])
        if len(params) is not 0:
            argument_list.append(params)
            index_params.append(i)
    # print(str(arguments))
    # print(str(argument_list))

    if test:
        limit = 2
    print()
    for i, input_filename in enumerate(os.listdir(input_dir)):
        output_filename = input_filename
        if prefix:
            if input_filename.startswith(prefix):
                continue
            else:
                output_filename = "{}_{}".format(prefix, input_filename)

        input_name, input_extension = os.path.splitext(input_filename)

        if images:
            extensions = [".jpg", ".png", ".gif"]
            is_an_image = any(input_filename.lower().endswith(e)
                              for e in extensions)
            if is_an_image:

                # input_file = input_filename  # os.path.join(input_dir, input_filename)
                # output_file = os.path.join(input_dir, output_filename)

                # Load image
                img = Image.open(input_filename)
                arguments_template = arguments.copy()
                for i, _ in enumerate(argument_list):
                    for arg in argument_list[i]:
                        arguments_template[index_params[i]] = arguments_template[index_params[i]].replace("<{}>".format(arg), str(eval(arg)))
                command_arguments = ''
                for arg in arguments_template:
                    command_arguments += arg + ' '

                command = (script + " %s") % (command_arguments)
                print(command)

                # Run command
                try:
                    os.system(command)
                except:
                    print("error running command")
                    raise
                if test and i == limit:
                    return

                print()

if __name__ == "__main__":
    # This will only be executed when this module is run direcly
    from docopt import docopt
    main(docopt(__doc__))
