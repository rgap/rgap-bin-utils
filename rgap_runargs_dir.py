#!/usr/bin/env python3
"""Run a script with its arguments using the files from the current directory

Usage:
    rgap_runargs_dir.py <script> <arguments> [--filetypes=<filetypes>] [--prefix=<prefix>] [--test]

    rgap_runargs_dir.py -h

Arguments:
    script          script to run
    arguments       arguments

Options:
    --test          for testing this command
    filetypes       types jpg,png,gif

Examples:
    rgap_runargs_dir.py convert "<input_filename> -crop <object.width>x<object.height>-0-15 <output_filename>" --prefix=conv --filetypes "jpg,png,gif"
    rgap_runargs_dir.py "ffmpeg" " -i <input_filename> <output_filename>.mp3" --filetypes "mp4"
    rgap_runargs_dir.py "ffmpeg" " -i <input_filename> -filter:v scale=800:-1 -c:a copy <output_filename>" --filetypes "mp4" --prefix="v"
    rgap_runargs_dir.py "ffmpeg" " -i '<input_filename>' -vf 'scale=iw/2:ih/2' -c:v libx264 -c:a copy '<output_filename>.mp4'" --filetypes "ts"

"""

import os
import re
from PIL import Image, ImageChops

def runcommand(script, arguments, input_filename, output_filename, argument_list, index_params, test, obj):
    # input_file = input_filename  # os.path.join(input_dir, input_filename)
    # output_file = os.path.join(input_dir, output_filename)

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


def main(args):
    script = args['<script>']
    arguments = args['<arguments>']
    filetypes = args['--filetypes']
    prefix = args['--prefix']
    test = args['--test']

    if filetypes:
        extensions = ['.' + ftype for ftype in filetypes.split(',')]

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

        if filetypes:
            is_the_type = any(input_filename.lower().endswith(e)
                              for e in extensions)
            if is_the_type:
                # Special case when it's an image
                obj = None
                if "jpg" in input_filename or "png" in input_filename or "gif" in input_filename:
                    # Load image
                    obj = Image.open(input_filename)

                runcommand(script, arguments, input_filename, output_filename, argument_list, index_params, test, obj)
        else:
            runcommand(script, arguments, input_filename, output_filename, argument_list, index_params, test, obj)
                

if __name__ == "__main__":
    # This will only be executed when this module is run direcly
    from docopt import docopt
    main(docopt(__doc__))
