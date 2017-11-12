#!/usr/bin/env python3
"""This downloads files from a website. To install chromedriver run: "brew install chromedriver".

Usage:
    rgap_getfiles.py <tag_name> <attr_name> <extension> <base_url> [--prefix=<prefix>]

    rgap_getfiles.py -h

Arguments:
    tag_name        tag name to search for; e.g. a, audio, etc
    attr_name       attribute name that contains the file url; e.g. href, src, etc
    extension       extension of the file name to download; e.g. pdf, wav, or pdf,wav etc
    base_url        url that contains the files to download
    prefix          adds a prefix, and it will number the files as it finds them

"""

from bs4 import BeautifulSoup
from selenium import webdriver
from urllib.request import urlretrieve
from urllib.parse import urlparse, urljoin
from urllib.error import HTTPError, URLError
import urllib.request
import re
import os


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
    print('filename: ', filename)
    print('Downloading:', url)
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
            print('HTTP Error:', e.code, url)
        except (URLError, e):
            print('URL Error:', e.reason, url)

        # Open our local file for writing
        # with open(filename, 'wb') as local_file:
        #     local_file.write(f.read())


def main(args):

    base_url = args['<base_url>']
    tag_name = args['<tag_name>']
    attr_name = args['<attr_name>']
    extension = args['<extension>']
    prefix = args['--prefix']

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

    # only urls with files with certain extensions
    list_fileurls_withextension = []
    for url in list_fileurls:
        for ext in list_extensions:
            if re.search(ext,  url.lower()):
                list_fileurls_withextension.append(url)

    with open('info.txt', 'a') as local_file:
        try:
            print("\nFound %s/%s urls %s" % (len(list_fileurls_withextension),
                                              len(list_fileurls), base_url))
            for index, url in enumerate(list_fileurls_withextension, start=1):
                local_file.write(base_url + ' --- ' + url + '\n')
                if prefix is not None:
                    if len(list_fileurls_withextension) == 1:
                        filename = prefix
                    else:
                        filename = prefix + '_' + str(index)
                else:
                    filename = None
                download(urljoin(base_url, url), filename)
        except:
            print("Error downloading:", tag_name, attr_name, extension, base_url)

if __name__ == "__main__":
    # This will only be executed when this module is run direcly
    from docopt import docopt
    main(docopt(__doc__))
