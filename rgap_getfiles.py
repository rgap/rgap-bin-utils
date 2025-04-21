#!/usr/bin/env python3
"""
This downloads files from a website. To install chromedriver run: "brew install chromedriver".

Usage:
    rgap_getfiles.py <tag_name> <attr_name> <extension> <base_url> [--content_tag] [--download_again] [--selenium] [--selenium_download] [--unique_names] [--parallel] [--workers=<num>] [--prefix=<prefix>] [--headless] [--sel_wait] [--sel_waitscroll] [--nocookies]
    rgap_getfiles.py <tag_name> <attr_name> <extension> <base_url> <xpaths>

    rgap_getfiles.py -h

Arguments:
    tag_name              tag name to search for; e.g. a, audio, etc
    attr_name             attribute name that contains the file url; e.g. href, src, etc
    extension             extension of the file name to download; e.g. pdf, wav, or pdf,wav
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
    unique_names          if file exists, append _1, _2… to the filename instead of skipping
    parallel              download files in parallel using threads
    workers               number of parallel workers (default: number of CPU cores)

Examples:
    rgap_getfiles.py a href .pdf https://example.com --parallel --workers=10
"""

import operator
import os
import re
import shutil
import sys
import time
import unicodedata
import threading
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urljoin, urlparse
from urllib.request import Request, urlopen

import gdown
import pyperclip
import requests
from bs4 import BeautifulSoup
from docopt import docopt
from lxml import html
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from w3lib import url as w3_url
import concurrent.futures


def slugify(value, allow_unicode=False):
    """
    Convert text to a safe filename.
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


def download(url, filename=None, download_again=False, unique_names=False):
    if "drive.google.com" in url:
        download_from_gdrive(url, filename, download_again, unique_names)
    elif "docs.google.com" in url and "/presentation" in url:
        download_from_gdocs(url, filename, download_again, unique_names)
    elif "github.com" in url:
        download_from_github(url, filename, download_again, unique_names)
    else:
        download_file(url, filename, download_again, unique_names)


def download_from_github(url, filename=None, download_again=False, unique_names=False):
    uc_url = url.replace("blob", "raw")
    download_file(uc_url, filename, download_again, unique_names)


def download_from_gdrive(url, filename=None, download_again=False, unique_names=False):
    if "file/d/" in url:
        m = re.search("file/d/(.*?)(/|$)", url)
        file_id = m.group(1)
    else:
        file_id = parse_qs(urlparse(url).query)["id"][0]
    uc_url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(uc_url, None, quiet=False)


def download_from_gdocs(url, filename=None, download_again=False, unique_names=False):
    clean = w3_url.url_query_cleaner(url)
    if "/export/pdf" in clean:
        uc_url = clean.replace("/export/pdf", "/present")
        direct = clean
    else:
        uc_url = clean
        direct = clean.replace("/present", "/export/pdf")
    page = requests.get(uc_url)
    soup = BeautifulSoup(page.text, "lxml")
    title = soup.find("meta", property="og:title")["content"]
    pdf_name = slugify(title) + ".pdf"
    download_file(direct, pdf_name, download_again, unique_names)


def download_file(url, filename=None, download_again=False, unique_names=False):
    name = urlparse(os.path.basename(url)).path
    # Determine initial filename
    if filename:
        ext = os.path.splitext(name)[1]
        filename = filename + ext
    else:
        filename = name

    # If unique naming requested, always find the next free name
    if unique_names:
        base, ext = os.path.splitext(filename)
        candidate = filename
        counter = 1
        while os.path.exists(candidate):
            candidate = f"{base}_{counter}{ext}"
            counter += 1
        filename = candidate
    # Otherwise skip if exists and not forced
    elif not download_again and os.path.exists(filename):
        print(f"Already exists: {filename}")
        return

    print(f"Saving as: {filename}")
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req) as r, open(filename, "wb") as f:
            shutil.copyfileobj(r, f)
    except Exception:
        os.system(f'wget --tries=3 -O "{filename}" "{url}"')


def get_files_urls(base_url, tree, tag_name, attr_name, extension):
    p = re.compile(r"(?:^|(?<=,))[^,]*")
    tags = tree if tag_name is None else [t for name in re.findall(p, tag_name) for t in tree.iter(name)]
    urls = {t.attrib[a] for t in tags for a in re.findall(p, attr_name) if a in t.attrib}
    if not extension:
        return list(urls)
    exts = re.findall(p, extension.lower().strip(","))
    out = [u for u in urls if any(ext in u.lower() for ext in exts) or ("drive.google.com" in u and "drive" in extension)]
    print(f"Found {len(out)} items out of {len(urls)} tags at {base_url}")
    return out


def find_content_tag(tree):
    counts = {}
    for p in tree.iter("p"):
        parent = p.getparent()
        counts[parent] = counts.get(parent, 0) + 1
    return max(counts, key=counts.get)


def get_fullurl(base, url):
    return url if url.startswith(('http://', 'https://')) else urljoin(base, url)


def main(args):
    base_url       = args['<base_url>']
    tag_name       = args['<tag_name>']
    attr_name      = args['<attr_name>']
    extension      = args['<extension>']
    xpaths         = args.get('<xpaths>')
    prefix         = args.get('--prefix')
    use_content    = args.get('--content_tag')
    use_selenium   = args.get('--selenium')
    selenium_dl    = args.get('--selenium_download')
    sel_wait       = args.get('--sel_wait')
    sel_scroll     = args.get('--sel_waitscroll')
    headless       = args.get('--headless')
    download_again = args.get('--download_again')
    unique_names   = args.get('--unique_names')
    parallel       = args.get('--parallel')
    workers        = int(args.get('--workers')) if args.get('--workers') else (os.cpu_count() or 1)
    nocookies      = args.get('--nocookies')

    # setup Selenium if needed
    if use_selenium:
        chrome_opts = webdriver.ChromeOptions()
        chrome_opts.add_argument("--lang=en")
        if not nocookies:
            chrome_opts.add_argument("user-data-dir=~/.rgap_selenium")
        if headless:
            chrome_opts.add_argument("--headless")
        chrome_opts.add_experimental_option("prefs", {"download.default_directory": os.getcwd()})
        driver = webdriver.Chrome(service=Service("/usr/local/bin/chromedriver"), options=chrome_opts)
        driver.set_window_size(800, 600)
        driver.get(base_url)
        if sel_wait:
            time.sleep(5)
        if sel_scroll:
            for i in range(2, 0, -1):
                driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight/{i});")
                time.sleep(1)
        html_src = driver.page_source
    else:
        html_src = urlopen(Request(base_url, headers={"User-Agent": "Mozilla/5.0"})).read()

    tree = html.fromstring(html_src)
    if use_content:
        tree = find_content_tag(tree)

    urls = []
    if xpaths:
        for xp in xpaths.split(','):
            urls.extend(get_files_urls(base_url, tree.xpath(xp), None, attr_name, extension))
    else:
        urls = get_files_urls(base_url, tree, tag_name, attr_name, extension)

    lock = threading.Lock()
    def worker(item):
        idx, u = item
        with lock:
            with open('info.txt', 'a') as log:
                log.write(f"{base_url} --- {u}\n")
        fname = None
        if prefix:
            fname = prefix if len(urls) == 1 else f"{prefix}_{idx}"
        full = get_fullurl(base_url, u)
        if selenium_dl:
            driver.get(full)
            time.sleep(2)
        else:
            print(f"Downloading {full}")
            download(full, fname, download_again, unique_names)

    items = list(enumerate(urls, start=1))
    if parallel and not selenium_dl:
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
            ex.map(worker, items)
    else:
        for it in items:
            worker(it)

    if use_selenium:
        driver.quit()

if __name__ == '__main__':
    args = docopt(__doc__)
    main(args)
