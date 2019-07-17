#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Downloads a youtube audio

Usage:
    rgap_yt_getaudio.py <url>

    rgap_yt_getaudio.py -h

Arguments:
    url        url of the youtube video
"""

import youtube_dl
import os


class MyLogger(object):

    def debug(self, msg):
        pass

    def warning(self, msg):
        # if msg == 'video doesn\'t have subtitles':
        #     print 'Error: no subtitles'
        # else:
        #     print(msg)
        print(msg)

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading.')
    if d['status'] == 'error':
        print('Error')


def audio_downloader(url):
    ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        # info = ydl.extract_info(url)
        # file = ydl.prepare_filename(info)
        # print(info)
        # filename, file_extension = os.path.splitext(file)
        par = parse_qs(urlparse(url).query)
        filename = par['v'][0]
        ydl.download([url])  # the id should be exactly 11 characters

    return "{}".format(filename)


def main(args):
    url = args['<url>']

    file = audio_downloader(url)
    print(file)


if __name__ == "__main__":
    # This will only be executed when this module is run direcly
    from docopt import docopt
    main(docopt(__doc__))
