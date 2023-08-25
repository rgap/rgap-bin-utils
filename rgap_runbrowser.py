#!/usr/bin/env python3
import pickle

from selenium import webdriver

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("user-data-dir=/Users/rgap/rgap_bin/selenium_session")
chrome_options.add_argument("--lang=en")
browser = webdriver.Chrome("/usr/local/bin/chromedriver", chrome_options=chrome_options)
browser.get("https://m.facebook.com/")
