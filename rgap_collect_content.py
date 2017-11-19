#!/usr/bin/env python3
"""This gets content from within a tag given its "xpath" from a site and stores them into a csv file.

Usage:
    rgap_collect_content.py <base_url> <xpaths> [--csv=<csv>] [--r] [--attr=<attr>] [--lib_selenium]

    rgap_collect_content.py -h

Arguments:
    base_url        main url
    xpaths          xpaths (separated by commas) that direct to the tags
    csv             csv file where to store the xpath texts
    r               to reopen the same csv file
    attr            attributes (separated by commas) to get besides the text inside the tag e.g. href
    lib_selenium    use selenium chrome instead of urllib

Examples:
    rgap_collect_content.py http://www.english-test.net/toefl/listening/ /html/body/center/table[6]/tbody/tr/td[1]/table[1]/tbody/tr[2]/td[2]/table[1]/tbody/tr/td/a --csv=urls.csv --attr=href

"""

from selenium import webdriver
from urllib.parse import urlparse, urlunparse
import urllib.request
from lxml import html
import csv
import os


def csv_writer(data, attributes, path, reopen):
    """
    Write data to a CSV file path
    """
    reopen = 'a' if reopen else 'w'
    filexists = os.path.isfile(os.getcwd() + '/' + path)

    with open(path, reopen) as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        if not filexists:
            writer.writerow(attributes)
        for line in data:
            writer.writerow(line)


def full_url(base_url, href):

    full_url = href
    netloc = urlparse(full_url).netloc
    if netloc == '':
        domain = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(base_url))
        full_url = domain + href
    return full_url


def main(args):

    base_url = args['<base_url>']
    xpaths = args['<xpaths>']
    csv_output = args['--csv']
    attributes = args['--attr']
    reopen = args['--r']
    lib_selenium = args['--lib_selenium']

    xpaths = xpaths.split(',')
    if attributes is not None:
        attributes = attributes.split(',')

    if not lib_selenium:
        html_source = urllib.request.urlopen(base_url).read()
    else:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--lang=en")
        browser = webdriver.Chrome("/usr/local/bin/chromedriver", chrome_options=chrome_options)
        browser.get(base_url)
        html_source = browser.page_source
    tree = html.fromstring(html_source)

    data = []
    for xpath in xpaths:
        elements = tree.xpath(xpath)
        # print(elements)
        for e in elements:
            attr_list = []
            attr_list.append(e.text_content())
            if attributes is not None:
                for attr in attributes:
                    if attr == 'href':
                        attr_list.append(full_url(base_url, e.attrib['href']))
                    else:
                        attr_list.append(e.attrib[attr])
            data.append(attr_list)

    if csv_output is None:
        for d in data:
            if isinstance(d, list):
                print(', '.join(d))
            else:
                print(d)
    else:
        headers = ['text'] + attributes if attributes is not None else ['text']
        csv_writer(data, headers, csv_output, reopen)

    if lib_selenium:
        browser.close()

if __name__ == "__main__":
    # This will only be executed when this module is run direcly
    from docopt import docopt
    main(docopt(__doc__))
