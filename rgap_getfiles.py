#!/usr/bin/env python3
"""This downloads files from a website. To install chromedriver run: "brew install chromedriver".

Usage:
    rgap_getfiles.py <tag_name> <attr_name> <extension> <base_url> [--content_tag] [--download_again] [--selenium]  [--selenium_download][--headless] [--sel_wait] [--sel_waitscroll] [--prefix=<prefix>] [--nocookies]
    rgap_getfiles.py <tag_name> <attr_name> <extension> <base_url> <xpaths> 

    rgap_getfiles.py -h

Arguments:
    tag_name              tag name to search for; e.g. a, audio, etc
    attr_name             attribute name that contains the file url; e.g. href, src, etc
    extension             extension of the file name to download; e.g. pdf, wav, or pdf,wav etc
    base_url              url that contains the files to download
    prefix                adds a prefix, and it will number the files as it finds them
    xpath                 all tags within the xpaths separated by commas
    content_tag           automatically find the tag where the content is
    selenium              use selenium
    selenium_download     download by getting the url with selenium
    sel_wait              long selenium wait
    sel_waitscroll        long selenium wait + scroll
    headless              run selenium driver without opening a window
    download_again        download even if the file exists

Examples:
    rgap_getfiles.py img src .jpg,.png,.gif https://www.buzzfeed.com/elainawahl/fotos-de-animales-que-capturan-perfectamente-tu-37b0u '//*[@id="mod-buzz-1"]/article' --selenium --sel_wait --selenium_download
    rgap_getfiles.py img src .jpg,.png,.gif https://rolloid.net/25-cosas-increibles-que-no-sabias-que-existian/
    rgap_getfiles.py a href "" https://easychair.org/conferences/submissions?a=21984264 '//tr/td[@class="center"][2]/a' --selenium --selenium_download
    rgap_getfiles.py a href .pdf 'https://web.stanford.edu/group/sisl/k12/optimization' --selenium --sel_wait --download_again
    rgap_getfiles.py a href .pdf,.doc,.dvi,.ppt,.pptx,.R,.py,.m,.mdl,.ipynb,.m,.zip,.csv,/pdf,/present https://laurentlessard.com/teaching/204-data-science-engineering/ --selenium --sel_wait --download_again

"""

import operator
import os
import pickle
import re
import shutil
import time
import unicodedata
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urljoin, urlparse
from urllib.request import Request, urlopen

import gdown
import pyperclip
import requests
from bs4 import BeautifulSoup
from lxml import html
from selenium import webdriver
from w3lib import url as w3_url


def slugify(value, allow_unicode=False):
    """
    To get a valid filename
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")


def download(url, filename=None, download_again=False):
    if "drive.google.com" in url:
        download_from_gdrive(url, filename=filename, download_again=download_again)
    elif "docs.google.com" in url and "/presentation" in url:
        download_from_gdocs(url, filename=filename, download_again=download_again)
    elif "github.com" in url:
        download_from_github(url, filename=filename, download_again=download_again)
    else:
        download_file(url, filename=filename, download_again=download_again)


def download_from_github(url, filename=None, download_again=False):
    uc_url = url.replace("blob", "raw")
    # print('Downloading', uc_url)
    download_file(uc_url, filename=filename, download_again=download_again)


def download_from_gdrive(url, filename=None, download_again=False):
    if "file/d/" in url:
        file_id = re.search("file/d/(.*)/", url)
        file_id = file_id if file_id else re.search("file/d/(.*)", url)
        file_id = file_id.group(1)
    else:
        parsed = urlparse(url)
        file_id = parse_qs(parsed.query)["id"][0]
    uc_url = "https://drive.google.com/uc?id=" + file_id
    # print('Downloading', uc_url)
    gdown.download(uc_url, None, quiet=False)


def download_from_gdocs(url, filename=None, download_again=False):
    url = w3_url.url_query_cleaner(url)
    url_direct_download = None
    if "/export/pdf" in url:
        uc_url = "/present".join(url.rsplit("/export/pdf", 1))
        url_direct_download = url
    else:
        uc_url = url
        url_direct_download = "/export/pdf".join(url.rsplit("/present", 1))
    # print('uc_url', uc_url)
    # print('url_direct_download', url_direct_download)

    page = requests.get(uc_url)
    soup = BeautifulSoup(page.text, "lxml")
    title = soup.find("meta", property="og:title")
    # print('title', title)
    filename = slugify(title["content"]) + ".pdf"
    print("download_from_gdocs - filename", filename)

    download_file(url_direct_download, filename=filename, download_again=download_again)


def download_file(url, filename=None, download_again=False):
    urlfile = urlparse(os.path.basename(url)).path
    if filename is None:
        filename = urlfile
    else:
        extension = os.path.splitext(urlfile)[1]
        filename += extension
    if not download_again and os.path.isfile(filename):
        print("Already exists", filename)
        return 0
    print("filename: ", filename)
    print("Downloading:", url)
    # Open the url
    try:
        print("with urllib")
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req) as response, open(
            os.getcwd() + "/" + filename, "wb"
        ) as out_file:
            shutil.copyfileobj(response, out_file)

        # urllib.request.urlretrieve(url, filename)
    except:
        print("urllib failed")
        try:
            print("with wget")
            # Quick solution for stopping this command https://stackoverflow.com/questions/43380562/python-script-cant-be-terminated-through-ctrlc-or-ctrlbreak
            # for i in range(0,360, step):
            os.system('wget --tries=5 -O "{0}" "{1}"'.format(filename, url))
            # time.sleep(0.2)
        # except KeyboardInterrupt:
        #     print("Stop me!")
        #     sys.exit(0)
        # handle errors
        except (HTTPError, e):
            print("HTTP Error:", e.code, url)
        except (URLError, e):
            print("URL Error:", e.reason, url)

        # Open our local file for writing
        # with open(filename, 'wb') as local_file:
        #     local_file.write(f.read())


def get_files_urls(base_url, tree, tag_name, attr_name, extension):
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
        # special urls
        if "drive" in extension:
            extension = extension.replace("drive", "")
            for url in list_fileurls:
                if "drive.google.com" in url:
                    list_fileurls_withextension.append(url)
        # if there are other extensions
        if extension != "":
            if extension[-1] == ",":
                extension = extension[0:-1]
            elif extension[0] == ",":
                extension = extension[1:]
            # only urls with files with certain extensions
            list_extensions = re.findall(p, extension.lower())
            for url in list_fileurls:
                for ext in list_extensions:
                    # ext = '.' + ext
                    # print('Find ' + ext + ' in ' + url.lower())
                    if ext in url.lower():
                        list_fileurls_withextension.append(url)

    print(
        "\nFound %s requested items out of %s tags %s"
        % (len(list_fileurls_withextension), len(list_fileurls), base_url)
    )

    # exit(0)
    return list_fileurls_withextension


def find_content_tag(tree):
    dict_ps = {}
    for tree_tag in tree.iter("p"):
        # print(id(tree_tag.getparent()))
        parent = tree_tag.getparent()
        if parent in dict_ps:
            dict_ps[parent] += 1
        else:
            dict_ps[parent] = 0
    # print(dict_ps)
    return max(dict_ps.items(), key=operator.itemgetter(1))[0]


def selenium_wait(driver, sleep_time):
    time.sleep(sleep_time)


def selenium_scrollbottom(driver, times, sleep_interval):
    # To be a bit more sure it loads it all
    for i in range(1, times):
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight/{});".format(times - i)
        )
        time.sleep(sleep_interval)


def get_fullurl(base_url, url):
    if "https://" in url or "http://" in url:
        full_url = url
    else:
        # full_url = base_url + '/' + url
        full_url = urljoin(base_url, url)
    return full_url


def main(args):
    base_url = args["<base_url>"]
    tag_name = args["<tag_name>"]
    attr_name = args["<attr_name>"]
    extension = args["<extension>"]
    xpaths = args["<xpaths>"]
    prefix = args["--prefix"]
    content_tag = args["--content_tag"]
    selenium = args["--selenium"]
    selenium_download = args["--selenium_download"]
    sel_wait = args["--sel_wait"]
    sel_waitscroll = args["--sel_waitscroll"]
    headless = args["--headless"]
    download_again = args["--download_again"]

    nocookies = args["--nocookies"]

    if selenium:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--lang=en")
        if not nocookies:
            chrome_options.add_argument(
                "user-data-dir=/Users/rgap/rgap_bin/selenium_session"
            )
        if headless:
            chrome_options.add_argument("--headless")

        # default download folder
        prefs = {
            "download.default_directory": os.getcwd(),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False,
            "safebrowsing.disable_download_protection": True,
        }
        chrome_options.add_experimental_option("prefs", prefs)
        driver = webdriver.Chrome(
            "/usr/local/bin/chromedriver", chrome_options=chrome_options
        )
        driver.set_window_size(500, 500)

        driver.get(base_url)
        if sel_wait:
            selenium_wait(driver, 5)
        if sel_waitscroll:
            selenium_scrollbottom(driver, 10, 5)

        html_source = driver.page_source
    else:
        req = Request(base_url, headers={"User-Agent": "Mozilla"})
        html_source = urlopen(req).read()

    tree = html.fromstring(html_source)
    # pyperclip.copy(html_source)

    # Get tag that contains the main post content
    if content_tag:
        tree = find_content_tag(tree)

    list_urls = []
    if xpaths:
        xpaths = xpaths.split(",")
        for xpath in xpaths:
            elements = tree.xpath(xpath)
            list_urls += get_files_urls(base_url, elements, None, attr_name, extension)
    else:
        list_urls += get_files_urls(base_url, tree, tag_name, attr_name, extension)

    # print(list_urls)

    with open("info.txt", "a") as local_file:
        try:
            for index, url in enumerate(list_urls, start=1):
                local_file.write(base_url + " --- " + url + "\n")
                if prefix is not None:
                    if len(list_urls) == 1:
                        filename = prefix
                    else:
                        filename = prefix + "_" + str(index)
                else:
                    filename = None

                full_url = get_fullurl(base_url, url)

                if selenium_download:  # TODO
                    driver.get(full_url)
                    time.sleep(2000)
                else:
                    print(full_url)
                    download(full_url, filename, download_again)
        except:
            print("Error downloading:", tag_name, attr_name, extension, base_url)


if __name__ == "__main__":
    # This will only be executed when this module is run direcly
    from docopt import docopt

    main(docopt(__doc__))
