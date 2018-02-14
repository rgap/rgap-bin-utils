#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""It cleans a subtitles file.

Usage:
    rgap_subtitles.py <input> <output> [--header=<header>]
    rgap_subtitles.py <input> [--header=<header>]

    rgap_subtitles.py -h

Arguments:
    input   input subtitles file path
    output  output subtitles file path
    header  what to write in the beginning
"""

import re
import os


def is_time_stamp(l):
    if l[:2].isnumeric() and l[2] == ':':
        return True
    return False


def has_letters(line):
    if re.search('[a-zA-Z]', line):
        return True
    return False


def has_no_text(line):
    l = line.strip()
    if not len(l):
        return True
    if l.isnumeric():
        return True
    if is_time_stamp(l):
        return True
    # if l[0] == '(' and l[-1] == ')':
    #     return True
    if not has_letters(line):
        return True
    return False


def is_lowercase_letter_or_comma(letter):
    if letter.isalpha() and letter.lower() == letter:
        return True
    if letter == ',':
        return True
    return False


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


def clean_up(lines):
    """
    Get rid of all non-text lines and
    try to combine text broken into multiple lines
    """
    flag = True
    new_lines = []
    for line in lines:
        # start adding lines since the first timestamp
        if flag and line[:3] == '00:':
            flag = False
        if flag:
            continue

        line = cleanhtml(line)
        if has_no_text(line):
            continue
        elif len(new_lines) and is_lowercase_letter_or_comma(line[0]):
            # combine with previous line
            new_lines[-1] = new_lines[-1].strip() + ' ' + line
        else:
            # append line
            new_lines.append(line)
    return new_lines


def main(args):

    input_file = args['<input>']
    output_file = args['<output>']
    header = args['--header']

    file_encoding = 'utf-8'
    with open(input_file, encoding=file_encoding, errors='replace') as f:
        lines = f.readlines()
        new_lines = clean_up(lines)
    if not output_file:
        output_file = os.path.splitext(input_file)[0] + '.txt'
    with open(output_file, 'w') as f:
        if header:
            f.write(header + '\n')
        f.write(input_file + '\n\n')
        for i, line in enumerate(new_lines):
            f.write(str(i + 1) + '. ' + line)

if __name__ == "__main__":
    # This will only be executed when this module is run direcly
    from docopt import docopt
    main(docopt(__doc__))
