#!/usr/bin/env python3
"""This downloads files from a website. To install chromedriver run: "brew install chromedriver".

Usage:
    rgap_imagegray.py <tag_name> <attr_name> <extension> <base_url>

    rgap_imagegray.py -h

Arguments:
    tag_name        tag name to search for; e.g. a, audio, etc
    attr_name       attribute name that contains the file url; e.g. href, src, etc
    extension       extension of the file name to download; e.g. pdf, wav, or pdf,wav etc
    base_url        url that contains the files to download

"""

from bs4 import BeautifulSoup
from selenium import webdriver
from urllib.request import urlopen
from urllib.parse import urlparse, urljoin
from urllib.error import HTTPError, URLError
import re
import os


def download(url):
    namefile = os.path.basename(url)
    namefile = urlparse(namefile).path

    if os.path.isfile(namefile):
        print("Already exists", namefile)
        return 0
    # Open the url
    try:
        f = urlopen(url)
        print('Downloading:', url)
        # Open our local file for writing
        with open(namefile, 'wb') as local_file:
            local_file.write(f.read())
    # handle errors
    except (HTTPError, e):
        print('HTTP Error:', e.code, url)
    except (URLError, e):
        print('URL Error:', e.reason, url)


def main(args):

    base_url = args['<base_url>']
    tag_name = args['<tag_name>']
    attr_name = args['<attr_name>']
    extension = args['<extension>']

    chrome_options = webdriver.ChromeOptions();
    chrome_options.add_argument("--lang=en"); 
    browser = webdriver.Chrome("/usr/local/bin/chromedriver", chrome_options=chrome_options)
    browser.get(base_url)
    html_source = browser.page_source
    # html_source = urlopen(base_url)
    soup = BeautifulSoup(html_source, 'html.parser')

    p = re.compile("(?:^|(?<=,))[^,]*")
    list_tag_names = re.findall(p, tag_name)

    list_tags = []
    for name in list_tag_names:
        list_tags.extend(soup.find_all(name))

    # print(list_tags)

    list_attr_names = re.findall(p, attr_name)

    list_fileurls = []
    for tag in list_tags:
        for attr in list_attr_names:
            if tag.has_attr(attr):
                list_fileurls.append(tag[attr])

    list_fileurls = set(list_fileurls)
    list_extensions = re.findall(p, extension)

    with open('info.txt', 'a') as local_file:
        try:
            print("\nFrom:", base_url)
            for url in list_fileurls:
                for ext in list_extensions:
                    if re.search(ext,  url):
                        local_file.write(base_url + ' --- ' + url + '\n')
                        download(urljoin(base_url, url))
        except:
            print("Error downloading:", tag_name, attr_name, extension, base_url)

if __name__ == "__main__":
    # This will only be executed when this module is run direcly
    from docopt import docopt
    main(docopt(__doc__))
