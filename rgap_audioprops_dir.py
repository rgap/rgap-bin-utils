#!/usr/bin/env python3
"""This changes the properties of audio files in a directory.

Usage:
    rgap_audioprops_dir.py (--c|<input_dir>) <output_dir> <artist> <album> [--suffix]
    rgap_audioprops_dir.py (--c|<input_dir>) <artist> <album> [--suffix]

    rgap_audioprops_dir.py -h

Arguments:
    csv_input      csv file

"""

import eyed3
import os
import logging
logging.getLogger("eyed3.mp3.headers").setLevel(logging.CRITICAL)


def main(args):

    input_dir = args['<input_dir>']
    output_dir = args['<output_dir>']
    current_directory = args['--c']
    suffix = args['--suffix']
    artist = args['<artist>']
    album = args['<album>']

    # In case the current directory is the one used
    if current_directory:
        input_dir = os.getcwd()

    if not output_dir:
        output_dir = input_dir
    # If the output directory doesn't exist then create it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for input_filename in os.listdir(os.getcwd()):

        output_filename = input_filename

        input_name, input_extension = os.path.splitext(input_filename)
        name_suffix = input_extension
        # Add suffix if necessary
        if suffix:
            name_suffix = "_props" + name_suffix
            if name_suffix in input_filename:
                continue
        output_filename = input_name + name_suffix

        extensions = ['.mp3', '.wav', '.wma', '.m4a', '.ogg']
        is_audio = any(input_extension.lower() == e
                       for e in extensions)
        if is_audio:
            input_file = os.path.join(input_dir, input_filename)
            output_file = os.path.join(output_dir, output_filename)

            print(input_file)
            audiofile = eyed3.load(input_file)
            audiofile.tag.artist = artist
            audiofile.tag.album = album
            audiofile.tag.album_artist = u""
            audiofile.tag.title = input_name
            audiofile.tag.track_num = 0

            audiofile.tag.save(output_file)

if __name__ == "__main__":
    # This will only be executed when this module is run direcly
    from docopt import docopt
    main(docopt(__doc__))