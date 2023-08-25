#!/usr/bin/env python3
"""This downloads a file from a url

Usage:
    rgap_getanyfile_url.py <base_url> <name> [--short] [--prefix=<prefix>]

    rgap_getanyfile_url.py -h

Arguments:
    base_url        url that contains the file to download
    name            filename
    prefix          prefix to put to the file (for more advanced purposes)

"""

import os
import urllib.request
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import urlopen, urlretrieve

from bs4 import BeautifulSoup
from selenium import webdriver


def download(url, filename=None):
    urlfile = urlparse(os.path.basename(url)).path
    if filename is None:
        filename = urlfile
    else:
        extension = os.path.splitext(urlfile)[1]
        filename += extension
    if os.path.isfile(filename):
        print("Already exists", filename)
        return 0
    print("filename: ", filename)
    print("Downloading:", url)
    # Open the url
    try:
        print("with urllib")
        urllib.request.urlretrieve(url, filename)
    except:
        try:
            print("with wget")
            os.system("wget -O {0} {1}".format(filename, url))
        # handle errors
        except (HTTPError, e):
            print("HTTP Error:", e.code, url)
        except (URLError, e):
            print("URL Error:", e.reason, url)

        # Open our local file for writing
        # with open(filename, 'wb') as local_file:
        #     local_file.write(f.read())


def main(args):
    base_url = args["<base_url>"]
    name = args["<name>"]
    short = args["--short"]
    prefix = args["--prefix"]

    if short:
        partition = name.split(" ")
        name = partition[0] + "_" + partition[1]

    print(urlopen(base_url).getheader("Content-Type"))
    try:
        if prefix is not None:
            name = "{}_{}".format(prefix, name)
        download(base_url, name)
    except:
        print("Error downloading:", base_url)


if __name__ == "__main__":
    # This will only be executed when this module is run direcly
    from docopt import docopt

    main(docopt(__doc__))
