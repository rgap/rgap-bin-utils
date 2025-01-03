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

import os
import re
from urllib.parse import parse_qs, urlparse
import difflib
import yt_dlp as youtube_dl

class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        print(msg)

    def error(self, msg):
        print(msg)

def my_hook(d):
    if d["status"] == "finished":
        print("Done downloading.")
    if d["status"] == "error":
        print("Error")

def subtitle_downloader(url, lang):
    subtitle_tmpl = "%(title)s_%(id)s.%(ext)s"  # Correct template syntax
    ydl_opts = {
        "logger": MyLogger(),
        "progress_hooks": [my_hook],
        "subtitlesformat": "vtt",
        "subtitleslangs": [lang],
        "skip_download": True,
        "writeautomaticsub": True,
        "outtmpl": subtitle_tmpl,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        video_title = info_dict.get("title", "Untitled")  # Default to "Untitled" if title is missing
        video_id = info_dict.get("id", "unknown_id")  # Default to "unknown_id" if ID is missing
        print("video_title:", video_title)
        filename = re.sub(r"[\s]*[:]+[\s]*", " - ", video_title)
        filename = re.sub(r"[\s]*[\|]+[\s]*", " _ ", filename)
        filename = re.sub(r'["]+', "'", filename)
        filename = re.sub(r"[?]+", "", filename)
        print("processed:", filename)
    return "{}_{}.{}.vtt".format(filename, video_id, lang)

def find_most_similar_filename(target_file):
    files_in_dir = os.listdir('.')
    closest_match = difflib.get_close_matches(target_file, files_in_dir, n=1)
    if closest_match:
        print(f"File '{target_file}' not found. Using the most similar file: {closest_match[0]}")
        return closest_match[0]
    print(f"File '{target_file}' not found and no similar files detected. Proceeding with the original name.")
    return target_file

def clean_subs(file_name, header):
    print("Cleaning")
    similar_file = find_most_similar_filename(file_name)
    similar_file = similar_file.replace('"', "'")
    cmd = ["rgap_subtitles_clean.py", '"{}"'.format(similar_file), "--header=" + header]
    os.system(" ".join(cmd))

def main(args):
    url = args["<url>"]
    lang = args["--lang"]
    if lang is None:
        lang = "en"

    subtitles_file = subtitle_downloader(url, lang)
    print(subtitles_file)
    clean_subs(subtitles_file, url)

if __name__ == "__main__":
    from docopt import docopt

    main(docopt(__doc__))
