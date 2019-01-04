#!/usr/bin/env python3
"""This gets content from within a tag given its "xpath" from a site and stores them into a csv file.

Usage:
    rgap_get_content.py <base_url> <xpaths> [--csv=<csv>] [--r] [--attr=<attr>] [--lib_selenium] [--cookies=<cookies>] [--trimtext] [--xpathcols] [--nchildnodes=<nchildnodes>] [--scrollbottom]

    rgap_get_content.py -h

Arguments:
    base_url        main url
    xpaths          xpaths (separated by commas) that direct to the tags
    csv             csv file where to store the xpath texts
    r               to reopen the same csv file
    attr            attributes (separated by commas) to get besides the text inside the tag e.g. href
    lib_selenium    use selenium chrome instead of urllib
    xpathcols       make a column per xpath

Examples:
    rgap_get_content.py http://www.english-test.net/toefl/listening/ '/html/body/center/table[6]/tbody/tr/td[1]/table[1]/tbody/tr[2]/td[2]/table[1]/tbody/tr/td/a' --csv=urls.csv --attr=href --lib_selenium

    rgap_get_content.py https://m.facebook.com/search/groups/?q="venta" "//div[@data-module-result-type='group']/div/div/div/div/div/div/div[@data-nt='NT:BOX'][2]" --lib_selenium --csv=output.csv --nchildnodes=3

    rgap_get_content.py https://m.facebook.com/search/groups/?q="venta" "//div[@data-module-result-type='group']/div/div/div/div/div/div/div/div[@data-nt='FB:TEXT4'][1],//div[@data-module-result-type='group']/div/div/div/div/div/div/div/div[@data-nt='FB:TEXT4'][2]" --lib_selenium --csv=output.csv

"""

from slugify import slugify
from selenium import webdriver
from urllib.parse import urlparse, urlunparse
from w3lib.url import url_query_cleaner
import urllib.request
import pickle
from lxml import html
import time
import csv
import os


def csv_writer(data, attributes, path, reopen, trimtext, columns):
    """
    Write data to a CSV file path
    """
    reopen = 'a' if reopen else 'w'
    filexists = os.path.isfile(os.getcwd() + '/' + path)

    with open(path, reopen) as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        if reopen == "w":
            writer.writerow(attributes)
        if columns:
            writer.writerows(data)
        else:
            for line in data:
                if trimtext:
                    line = line.replace('\n', ' ')[:50]
                    line = slugify(line)
                writer.writerow(line)


def full_url(base_url, href):

    full_url = href
    netloc = urlparse(full_url).netloc
    if netloc == '':
        domain = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(base_url))
        full_url = domain + href
    return full_url

def scroll_bottom(driver):

    SCROLL_PAUSE_TIME = 4
    while True:
        # Get scroll height
        ### This is the difference. Moving this *inside* the loop
        ### means that it checks if scrollTo is still scrolling 
        last_height = driver.execute_script("return document.body.scrollHeight")
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            # try again (can be removed)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)
            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            # check if the page height has remained the same
            if new_height == last_height:
                # if so, you are done
                break
            # if not, move on to the next loop
            else:
                last_height = new_height
                continue

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def main(args):

    base_url = args['<base_url>']
    xpaths = args['<xpaths>']
    csv_output = args['--csv']
    attributes = args['--attr']
    reopen = args['--r']
    lib_selenium = args['--lib_selenium']
    trimtext = args['--trimtext']
    xpathcols = args['--xpathcols']
    nchildnodes = int(args['--nchildnodes'])
    scrollbottom = args['--scrollbottom']

    cookies = args['--cookies']

    xpaths = xpaths.split(',')
    if attributes is not None:
        attributes = attributes.split(',')

    if not lib_selenium:
        html_source = urllib.request.urlopen(base_url).read()
    else:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("user-data-dir=selenium")  # Save session
        chrome_options.add_argument("--lang=en")
        browser = webdriver.Chrome("/usr/local/bin/chromedriver", chrome_options=chrome_options)
        if cookies:
            browser.get(base_url)
            for cookie in pickle.load(open(cookies, "rb")):
                browser.add_cookie(cookie)
        browser.get(base_url)
        if scrollbottom:
            scroll_bottom(browser)
        html_source = browser.page_source
    tree = html.fromstring(html_source)
    # print(html_source)

    data = []
    for xpath in xpaths:
        elements = tree.xpath(xpath)
        # print("column size:", len(elements))
        for e in elements:
            if nchildnodes is not None:
                node_list = []
                children = e.getchildren()
                if len(children) >= nchildnodes:
                    for i in range(nchildnodes):
                        node_list.append(children[i].text_content())
                else:
                    node_list = ['' for i in range(nchildnodes)]
                    node_list[0] = children[0].text_content()
                # print(node_list)
                data.append(node_list)
            elif attributes is not None:
                attr_list = []
                attr_list.append(e.text_content())
                for attr in attributes:
                    if attr == 'href':
                        attr_list.append(full_url(base_url, e.attrib['href']))
                    else:
                        attr_list.append(e.get(attr))
                data.append(attr_list)
            else:
                data.append(e.text_content())
        

    if csv_output is None:
        for d in data:
            if isinstance(d, list):
                print(', '.join(d))
            else:
                print(d)
    else:
        if xpathcols:
            columnsize = len(elements)
            data = zip(*list(chunks(data, columnsize)))
            headers = ['t'+str(i) for i in range(len(xpaths))]
            csv_writer(data, headers, csv_output, reopen, trimtext, True)
        elif nchildnodes:
            headers = ['t'+str(i) for i in range(nchildnodes)]
            csv_writer(data, headers, csv_output, reopen, trimtext, True)
        else:
            headers = ['text'] + attributes if attributes is not None else ['text']
            csv_writer(data, headers, csv_output, reopen, trimtext, False)

    if lib_selenium:
        browser.close()

if __name__ == "__main__":
    # This will only be executed when this module is run direcly
    from docopt import docopt
    main(docopt(__doc__))
