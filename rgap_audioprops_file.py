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

import mutagen
from mutagen.id3 import ID3, ID3NoHeaderError
import os


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
            try:
                audiofile = ID3(input_file)
            except ID3NoHeaderError:
                audiofile = mutagen.File(input_file, easy=True)
                audiofile.add_tags()

        audiofile['artist'] = artist
        audiofile['album'] = album
        audiofile['title'] = input_name
        audiofile.save(output_file)
    else:
        print("It's not an audio file.")

if __name__ == "__main__":
    # This will only be executed when this module is run direcly
    from docopt import docopt
    main(docopt(__doc__))
