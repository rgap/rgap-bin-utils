import operator
import os
import re
import shutil
import ssl
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup
from lxml import html
from selenium import webdriver


def find_content_tag(soup, url_site):
    dict_ps = {}
    for tag in soup.find_all("a"):
        # parent = tree_tag.getparent()
        if url_site in str(tag):
            print(tag)
    return


url_site = "lazinesscure"

with open("lazinesscure_proLiveLinks.txt") as f:
    lines = f.readlines()
    for base_url in lines:
        read_html = True
        # print(line)
        # req = Request(base_url, headers={'User-Agent': 'Mozilla'})
        # code = urlopen(req).getcode()
        # print(code)
        base_url = base_url[0 : len(base_url) - 1]
        req = Request(
            base_url, headers={"X-Mashape-Key": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"}
        )
        gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)  # Only for gangstars

        try:
            code = urlopen(req, context=gcontext).getcode()
            print(code, end=" ")
        except URLError as e:
            read_html = False
            print(e.reason, end=" ")

        print(base_url)

        if read_html:
            html_source = urlopen(req, context=gcontext).read()
            soup = BeautifulSoup(html_source, "lxml")
            find_content_tag(soup, url_site)

        print()
