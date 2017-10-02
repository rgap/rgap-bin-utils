#!/usr/bin/env python3
"""This gets content from within a tag given its "xpath" from a site and stores them into a csv file.

Usage:
    rgap_get_tags.py <base_url> <xpath> [--csv <csv_output>] [--attr <attribute>]

    rgap_get_tags.py -h

Arguments:
    base_url        main url
    xpath           xpath that directs to the tag
    csv_output      csv file where to store the xpath texts
    attribute       attribute to get besides the text inside the tag
"""

from selenium import webdriver
from urllib.parse import urlparse, urlunparse
from lxml import html
import csv


def csv_writer(data, path):
    """
    Write data to a CSV file path
    """
    with open(path, "w") as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        for line in data:
            writer.writerow(line)


def full_url(base_url, href):

    full_url = href
    netloc = urlparse(full_url).netloc
    if netloc == '':
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(base_url))
        full_url = domain + href
    return full_url


def main(args):

    base_url = args['<base_url>']
    xpath = args['<xpath>']
    csv_output = args['<csv_output>']
    attribute = args['<attribute>']

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--lang=en")
    browser = webdriver.Chrome("/usr/local/bin/chromedriver", chrome_options=chrome_options)
    browser.get(base_url)
    html_source = browser.page_source
    tree = html.fromstring(html_source)
    elements = tree.xpath(xpath)

    data = []
    for e in elements:
        if attribute == 'href':
            data.append([e.text.strip(), full_url(base_url, e.attrib['href'])])
        else:
            data.append(e.text.strip())

    if csv_output is None:
        for d in data:
            if isinstance(d, list):
                print(', '.join(d))
            else:
                print(d)
    else:
        csv_writer(data, csv_output)

    browser.close()

if __name__ == "__main__":
    # This will only be executed when this module is run direcly
    from docopt import docopt
    main(docopt(__doc__))
