#!/usr/bin/env python3
"""This changes the properties of an audio file.

Usage:
    rgap_audioprops_file.py <artist> <album> <input_file>

    rgap_audioprops_file.py -h

Arguments:
    artist      artist property
    album       album property
    input_file  input audio file

"""

import eyed3
import os
import logging
logging.getLogger("eyed3.mp3.headers").setLevel(logging.CRITICAL)


def main(args):

    input_file = args['<input_file>']
    artist = args['<artist>']
    album = args['<album>']
    input_name, input_extension = os.path.splitext(input_file)

    extensions = ['.mp3', '.wav', '.wma', '.m4a', '.ogg']
    is_audio = any(input_extension.lower() == e
                   for e in extensions)
    if is_audio:
        print(input_file)
        audiofile = eyed3.load(input_file)
        audiofile.tag.artist = artist
        audiofile.tag.album = album
        audiofile.tag.album_artist = u""
        audiofile.tag.title = input_name
        audiofile.tag.track_num = 0

        audiofile.tag.save()
    else:
        print("It's not an audio file.")

if __name__ == "__main__":
    # This will only be executed when this module is run direcly
    from docopt import docopt
    main(docopt(__doc__))
