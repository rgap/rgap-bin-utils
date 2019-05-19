#!/usr/bin/env python3
from selenium import webdriver

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("user-data-dir=/Users/rgap/rgap_bin/selenium")
driver = webdriver.Chrome(chrome_options=chrome_options)
