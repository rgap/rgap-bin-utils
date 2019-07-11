#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This finds facebook groups or pages and saves them into a csv file

Usage:
    gh_fbfinder.py <query> [--csv=<csv>] [--r] [--attr=<attr>] [--trimtext] [--url_column] [--page_finder]

    gh_fbfinder.py -h

Arguments:
    query           query string to search
    csv             csv file where to store the xpath texts
    r               to reopen the same csv file
    attr            attributes (separated by commas) to get besides the text inside the tag e.g. href - This is for future add-ons
    url_column      add the link to the group or page and the id column (this takes a lot longer)
    trimtext        replace break lines with spaces
    page_finder     find pages instead of groups

Examples:
    gh_fbfinder.py meme

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
import re
import numpy as np


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

def add_url_columns(data, browser, page_finder, base_url):
    # selenium clicks
    fb_groupurls = []
    fb_groupids = []
    # fb_groupmembers = []
    if page_finder:
        clickables = browser.find_elements_by_xpath("//div[@data-module-result-type='page']/div")
    else:
        clickables = browser.find_elements_by_xpath("//div[@data-module-result-type='group']/div")
    print('#Groups:', len(clickables))
    for i in range(0, len(clickables)):
        clickables[i].click()
        time.sleep(1)
        group_url = url_query_cleaner(browser.current_url)
        print(group_url)
        fb_groupurls.append(group_url)
        fb_groupids.append(os.path.basename(group_url))

        # Accurate Find number of members
        # browser.get(group_url + '?view=info')
        # time.sleep(1)
        # num_members = browser.find_element_by_xpath('//div[@id="root"]/div[1]/div[1]/div[3]/div[1]/div[1]/div[2]/div/div[1]/h3').text.replace(' Members','').replace(' Member','')
        # fb_groupmembers.append(num_members)
        # print(num_members)
        # browser.execute_script("window.history.go(-2)")
        # time.sleep(1)
        # browser.execute_script("window.history.go(-2)")
        time.sleep(1)
        browser.execute_script("window.history.go(-1)")
        time.sleep(1)
        # print(browser.current_url, base_url)
        if browser.current_url != base_url:
            browser.get(base_url)
            time.sleep(1)
        scroll_bottom(browser)

        if page_finder:
            clickables = browser.find_elements_by_xpath("//div[@data-module-result-type='page']/div")
        else:
            clickables = browser.find_elements_by_xpath("//div[@data-module-result-type='group']/div")
    # return np.hstack((np.array(fb_groupurls).reshape(-1,1), np.array(fb_groupids).reshape(-1,1), np.array(fb_groupmembers).reshape(-1,1), np.array(data)))
    return np.hstack((np.array(fb_groupurls).reshape(-1,1), np.array(fb_groupids).reshape(-1,1), np.array(data)))

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def convert_to_number(x):
    x = x.split(' ')[-1].upper()
    total_stars = 0
    # print(x)
    if 'K' in x:
        if len(x) > 1:
            total_stars = float(x.split('K', 1)[0]) * 1000 # convert K to a thousand
    elif 'M' in x:
        if len(x) > 1:
            total_stars = float(x.split('M', 1)[0]) * 1000000 # convert M to a million
    elif 'B' in x:
        total_stars = float(x.split('B', 1)[0]) * 1000000000 # convert B to a Billion
    else:
        total_stars = int(x) # Less than 1000
    return int(total_stars)


def main(args):

    query = args['<query>']
    attributes = args['--attr']
    reopen = args['--r']
    trimtext = args['--trimtext']
    url_column = args['--url_column']
    page_finder = args['--page_finder']

    ## THESE XPATHS MAY HAVE TO CHANGE SOME TIME
    if page_finder:
        base_url = 'https://m.facebook.com/search/pages/?q=%22{}%22'.format(query)
        xpath = "//div[@data-module-result-type='page']/div/div/div/div/div/div/div"
        csv_output = "{}_{}.csv".format("p", query)
    else:
        base_url = 'https://m.facebook.com/search/groups/?q=%22{}%22'.format(query)
        xpath = "//div[@data-module-result-type='group']/div/div/div/div/div/div/div"
        csv_output = "{}_{}.csv".format("g", query)

    nchildnodes = 3

    if attributes is not None:
        attributes = attributes.split(',')

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("user-data-dir=selenium_session")  # Save session
    chrome_options.add_argument("--lang=en")
    browser = webdriver.Chrome("/usr/local/bin/chromedriver", chrome_options=chrome_options)
    browser.get(base_url)
    time.sleep(1)

    scroll_bottom(browser)

    time.sleep(1)
    html_source = browser.page_source
    tree = html.fromstring(html_source)
    # print(html_source)

    data = []
    elements = tree.xpath(xpath)
    print("#elements:",len(elements))

    for e in elements:
        if nchildnodes is not None:
            node_list = []
            ## THIS LINE MAY HAVE TO CHANGE SOME TIME
            # Title and numbers node
            title_and_numbers = e.getchildren()[0].getchildren()[0].getchildren()
            # Description node
            description_node = e.getchildren()
            ##
            if len(title_and_numbers) + 1 >= nchildnodes and "member" in title_and_numbers[1].text_content() or "like" in title_and_numbers[1].text_content():
                # Title
                node_list.append(title_and_numbers[0].text_content())
                # print(node_list)
                # Likes and Page Type
                if page_finder:
                    likes_type = title_and_numbers[1].text_content().lower().split(' like this · ')
                else:
                    likes_type = title_and_numbers[1].text_content().lower().split(' members · ')

                # print(likes_type)
                node_list.append(convert_to_number(likes_type[0]))
                if len(likes_type) == 1:
                    node_list.append("")
                else:
                    node_list.append(likes_type[1])
                # Description
                if len(description_node) > 1:
                    node_list.append(description_node[1].text_content())
                else:
                    node_list.append('')
                
            else:
                node_list = ['' for i in range(nchildnodes + 1)]
                node_list[0] = title_and_numbers[0].text_content()
            # print(node_list)
            data.append(node_list)

        # This is for future add-ons
        elif attributes is not None:
            print(attributes)
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

    if url_column:
        data = add_url_columns(data, browser, page_finder, base_url)

    if csv_output is None:
        for d in data:
            if isinstance(d, list):
                print(', '.join(d))
            else:
                print(d)
    else:
        if nchildnodes:
            headers = []
            if url_column:
                headers = headers + ['url','id']
            headers = headers + ['t'+str(i) for i in range(nchildnodes+1)]
            csv_writer(data, headers, csv_output, reopen, trimtext, True)
        else:
            headers = ['text'] + attributes if attributes is not None else ['text']
            csv_writer(data, headers, csv_output, reopen, trimtext, False)

    browser.close()

if __name__ == "__main__":
    # This will only be executed when this module is run direcly
    from docopt import docopt
    main(docopt(__doc__))
