#!/usr/bin/env python3
import ast
import re
import pyperclip
from os.path import expanduser
# from email.utils import parseaddr

home = expanduser("~")

with open(home + '/tmp_files/tmp.txt', mode='r') as file:
    content = file.read()
    content_array = ast.literal_eval(content)
    emails = []
    for s in content_array:
        match = re.search(r'[\w\.-]+@[\w\.-]+', s)
        if match is not None:
            emails.append(match.group(0))
        # print(parseaddr(email))
    emails_str = ",".join(emails)
    print("{} emails to clipboard".format(len(emails)))
    emails = set(emails)
    print("{} unique emails".format(len(emails)))
    pyperclip.copy(emails_str)
