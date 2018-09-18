#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""It cleans and adds tags to some content.

Usage:
    py <input>

    py -h

Arguments:
    input   input content file

"""

import re
from htmltag import strong
from htmltag import a
from htmltag import h2
import csv
import random
import datetime


def main(args):

    input_file = args['<input>']

    with open(input_file) as f:
        lines = f.readlines()
        input_text = ' '.join(lines)
        input_text = input_text.lstrip()

        output = re.sub(r'[\n ]{2,}', '\n\n', input_text)
        lines = output.split('\n')

        # csv output
        header = ['title', 'content', 'status', 'publish_date', 'categories', 'tags']
        writer = csv.writer(open("output.csv", 'w'))
        writer.writerow(header)

        rand_categories = ['']

        # 80 characters subheading <h2>
        processed_lines = []
        post_counter = 0
        post_title = ''
        current_content = []
        for line in lines:
            if line[:2] == '@@':
                # if it's not the first post to record, then save the current content and title
                if post_title != '':
                    post_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    writer.writerow([post_title, '\n'.join(current_content).strip(), 'draft', post_date, random.choice(rand_categories), ''])

                post_title = line[3:].strip()
                post_counter += 1
                current_content = []
            elif line[:5] != '#####' and len(line) <= 80 and len(line) >= 4 and not line[:2] == '@@' and not line.endswith('.') and not line.endswith(':') and not line.endswith('!') and not line.startswith('-'):
                line = h2(line)
            if line[:5] != '#####' and not line[:2] == '@@':
                current_content.append(line)
            processed_lines.append(line)

        # Save the only or the last post
        post_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([post_title, '\n'.join(current_content).strip(), 'draft', post_date, random.choice(rand_categories), ''])

        output = '\n'.join(processed_lines)

        text_file = open("output.txt", "w")
        text_file.write(output)
        text_file.close()


if __name__ == "__main__":
    # This will only be executed when this module is run direcly
    from docopt import docopt
    main(docopt(__doc__))
