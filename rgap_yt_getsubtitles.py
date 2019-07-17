#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Downloads a youtube video subtitles and cleans it

Usage:
    rgap_yt_getsubtitles.py <url> [--lang=lang]

    rgap_yt_getsubtitles.py -h

Arguments:
    url        url of the youtube video
    lang       language; e.g. en, es. It is English by default
"""

import youtube_dl
import os
from urllib.parse import urlparse, parse_qs


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


def subtitle_downloader(url, lang):
    subtitle_tmpl = '%(title)s.%(ext)s'
    ydl_opts = {
        'logger': MyLogger(),
        'progress_hooks': [my_hook],  # only works when downloading videos
        'subtitlesformat': 'vtt',
        'subtitleslangs': [lang],
        'skip_download': True,
        # 'allsubtitles': True,
        # 'writesubtitles': True,
        'writeautomaticsub': True,
        'outtmpl': subtitle_tmpl,  # DEFAULT_OUTTMPL = '%(title)s-%(id)s.%(ext)s'
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


def clean_subs(file_name, header):
    print("Cleaning")
    file_name.replace('"', "'")
    cmd = [
        "rgap_subtitles_clean.py",
        '"{}"'.format(file_name),
        "--header=" + header
    ]
    os.system(" ".join(cmd))


def main(args):
    url = args['<url>']
    lang = args['--lang']
    if lang is None:
        lang = 'en'

    subtitles_file = subtitle_downloader(url, lang)
    print(subtitles_file)
    clean_subs(subtitles_file, url)


if __name__ == "__main__":
    # This will only be executed when this module is run direcly
    from docopt import docopt
    main(docopt(__doc__))
