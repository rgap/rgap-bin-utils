#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Downloads a youtube audio

Usage:
    rgap_yt_getvideo.py <url> [--q=q]

    rgap_yt_getvideo.py -h

Arguments:
    url        url of the youtube video
    q          video quality

Examples:
    rgap_yt_getvideo.py https://www.youtube.com/watch?v=J---aiyznGQ --q=best
"""

import os
from urllib.parse import parse_qs, urlparse

import youtube_dl


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
    if d["status"] == "finished":
        print("Done downloading.")
    if d["status"] == "error":
        print("Error")


def video_downloader(url, quality):
    if quality == "best":
        # Download best mp4 format available or any other best if no mp4 available
        q = "bestvideo+bestaudio[ext=m4a]/best/best"
    elif quality == "medium":
        # Download best format available but no better than 480p
        q = "bestvideo[height<=480]+bestaudio/best[height<=480]"
    elif quality == "low":
        q = "bestvideo[height<=240]+bestaudio/best[height<=240]"

    ydl_opts = {
        "format": q,
        "postprocessors": [
            {
                "key": "FFmpegVideoConvertor",
                "preferedformat": "mp4",
            }
        ],
        "logger": MyLogger(),
        "progress_hooks": [my_hook],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        # info = ydl.extract_info(url)
        # file = ydl.prepare_filename(info)
        # print(info)
        # filename, file_extension = os.path.splitext(file)
        par = parse_qs(urlparse(url).query)
        filename = par["v"][0]
        ydl.download([url])  # the id should be exactly 11 characters

    return "{}".format(filename)


def main(args):
    url = args["<url>"]
    quality = args["--q"]

    file = video_downloader(url, quality)
    print(file)


if __name__ == "__main__":
    # This will only be executed when this module is run direcly
    from docopt import docopt

    main(docopt(__doc__))
