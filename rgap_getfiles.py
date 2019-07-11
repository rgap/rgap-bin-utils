#!/usr/bin/env python3
"""This downloads files from a website. To install chromedriver run: "brew install chromedriver".

Usage:
    rgap_getfiles.py <tag_name> <attr_name> <extension> <base_url> [--content_tag] [--selenium] [--headless] [--sel_wait] [--prefix=<prefix>] [--nocookies]
    rgap_getfiles.py <tag_name> <attr_name> <extension> <base_url> <xpaths> [--content_tag] [--selenium] [--headless] [--sel_wait] [--prefix=<prefix>] [--nocookies]

    rgap_getfiles.py -h

Arguments:
    tag_name        tag name to search for; e.g. a, audio, etc
    attr_name       attribute name that contains the file url; e.g. href, src, etc
    extension       extension of the file name to download; e.g. pdf, wav, or pdf,wav etc
    base_url        url that contains the files to download
    prefix          adds a prefix, and it will number the files as it finds them
    xpath           all tags within the xpaths separated by commas
    content_tag     automatically find the tag where the content is
    selenium        use selenium
    sel_wait        long selenium wait
    headless        run selenium driver without opening a window

Examples:
    rgap_getfiles.py img src jpg,png,gif https://www.buzzfeed.com/elainawahl/fotos-de-animales-que-capturan-perfectamente-tu-37b0u '//*[@id="mod-buzz-1"]/article' --selenium --sel_wait
    rgap_getfiles.py img src jpg,png,gif https://rolloid.net/25-cosas-increibles-que-no-sabias-que-existian/
    rgap_getfiles.py a href "" https://easychair.org/conferences/submissions?a=21984264 '//tr/td[@class="center"][2]/a' --selenium

"""

import pyperclip
from lxml import html
from selenium import webdriver
from urllib.request import Request, urlopen
from urllib.parse import urlparse, urljoin
from urllib.error import HTTPError, URLError
import pickle
import time
import operator
import shutil
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
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(req) as response, open(os.getcwd() + '/' + filename, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)

        # urllib.request.urlretrieve(url, filename)
    except:
        print("urllib failed")
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

def get_files_urls(driver, base_url, tree, tag_name, attr_name, extension):

    p = re.compile("(?:^|(?<=,))[^,]*")
    
    # If they are xpaths, then the tags (list_tags) were already found
    if tag_name is None:
        list_tags = tree
    else:
        list_tag_names = re.findall(p, tag_name)
        list_tags = []
        for name in list_tag_names:
            for tree_tag in tree.iter(name):
                list_tags.append(tree_tag)

    list_attr_names = re.findall(p, attr_name)

    list_fileurls = []
    for tag in list_tags:
        for attr in list_attr_names:
            if attr in tag.attrib:
                list_fileurls.append(tag.attrib[attr])

    list_fileurls = set(list_fileurls)

    list_fileurls_withextension = []
    if extension == "":
        list_fileurls_withextension = list_fileurls
    else:
        # only urls with files with certain extensions
        list_extensions = re.findall(p, extension)
        for url in list_fileurls:
            for ext in list_extensions:
                if re.search(ext,  url.lower()):
                    list_fileurls_withextension.append(url)

    print("\nFound %s requested items out of %s tags %s" % (len(list_fileurls_withextension),
                                     len(list_fileurls), base_url))

    return list_fileurls_withextension


def find_content_tag(tree):
    dict_ps = {}
    for tree_tag in tree.iter('p'):
        # print(id(tree_tag.getparent()))
        parent = tree_tag.getparent()
        if parent in dict_ps:
            dict_ps[parent] += 1
        else:
            dict_ps[parent] = 0
    # print(dict_ps)
    return max(dict_ps.items(), key=operator.itemgetter(1))[0]


def selenium_wait(driver, times, sleep_interval):
    # To be a bit more sure it loads it all
    for i in range(1, times):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/{});".format(times - i))
        time.sleep(sleep_interval)


def main(args):

    base_url = args['<base_url>']
    tag_name = args['<tag_name>']
    attr_name = args['<attr_name>']
    extension = args['<extension>']
    xpaths = args['<xpaths>']
    prefix = args['--prefix']
    content_tag = args['--content_tag']
    selenium = args['--selenium']
    sel_wait = args['--sel_wait']
    headless = args['--headless']

    nocookies = args['--nocookies']

    if selenium:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--lang=en")
        if not nocookies:
            chrome_options.add_argument("user-data-dir=/Users/rgap/rgap_bin/selenium_session") 
        if headless:
            chrome_options.add_argument("--headless")

        # default download folder
        prefs = {
            'download.default_directory': os.getcwd(),
            'download.prompt_for_download': False,
            'download.directory_upgrade': True,
            'safebrowsing.enabled': False,
            'safebrowsing.disable_download_protection': True}
        chrome_options.add_experimental_option('prefs', prefs)
        driver = webdriver.Chrome("/usr/local/bin/chromedriver", chrome_options=chrome_options)
        driver.set_window_size(500, 500)

        driver.get(base_url)
        if sel_wait:
            selenium_wait(driver, 10, 5)
        html_source = driver.page_source
    else:
        req = Request(base_url, headers={'User-Agent': 'Mozilla'})
        html_source = urlopen(req).read()

    tree = html.fromstring(html_source)
    # pyperclip.copy(html_source)


    # Get tag that contains the main post content
    if content_tag:
        tree = find_content_tag(tree)

    list_urls = []
    if xpaths:
        xpaths = xpaths.split(',')
        for xpath in xpaths:
            elements = tree.xpath(xpath)
            list_urls += get_files_urls(driver, base_url, elements, None, attr_name, extension)
    else:
        list_urls += get_files_urls(driver, base_url, tree, tag_name, attr_name, extension)

    # print(list_urls)

    with open('info.txt', 'a') as local_file:
        try:
            for index, url in enumerate(list_urls, start=1):
                local_file.write(base_url + ' --- ' + url + '\n')
                if prefix is not None:
                    if len(list_urls) == 1:
                        filename = prefix
                    else:
                        filename = prefix + '_' + str(index)
                else:
                    filename = None
                driver.get(urljoin(base_url, url))
                time.sleep(2000)
                # download(urljoin(base_url, url), filename)
        except:
            print("Error downloading:", tag_name, attr_name, extension, base_url)

if __name__ == "__main__":
    # This will only be executed when this module is run direcly
    from docopt import docopt
    main(docopt(__doc__))
