#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""It cleans and adds tags to some content. It can also simply convert markup to html.

Usage:
    gh_markup2html_lists.py <input> <itemstolist>
    gh_markup2html_lists.py <input> [--simplemarkup]
    
    gh_markup2html_lists.py -h

Arguments:
    input           input content file
    itemstolist     2 items to make bullet lists with
    simplemarkup    to simply convert markup to html

Example:
    gh_markup2html_lists.py input.txt
    gh_markup2html_lists.py input.txt --simplemarkup
    gh_markup2html_lists.py input.txt INGREDIENTES,PREPARACION
    
"""

import re
# from htmltag import strong
# from htmltag import a
# from htmltag import h2
import markdown2
import csv
import random
import datetime
from unidecode import unidecode


def rawstring(s):
    return unidecode(s.lower())


def main(args):

    input_file = args['<input>']
    itemstolist = args['<itemstolist>']
    simplemarkup = args['--simplemarkup']
    itemize_elements = False
    if itemstolist is not None:
        itemstolist = rawstring(itemstolist)
        items = itemstolist.split(',')
        itemize_elements = True  # if there are lines to be itemized

    rand_categories = ['']

    # csv output
    header = ['title', 'content', 'status', 'publish_date', 'categories', 'tags']
    writer = csv.writer(open("output.csv", 'w'))
    writer.writerow(header)

    with open(input_file) as f:
        full_content = f.read()
        posts = full_content.split('&&&&!')
        post_list = []

        for post in posts:
            post_title = ''
            post = post.lstrip()
            post = re.sub(r'[\n ]{2,}', '\n\n', post)

            lines = post.split('\n')
            processed_lines = []
            copy = False

            flagendinglist = False
            for line in lines:
                if not simplemarkup:
                    line = line.lstrip('#-. ')

                if itemize_elements and rawstring(line).startswith(items[0]):
                    # print('start')
                    processedline = '## ' + line
                    processed_lines.append(processedline.upper())
                    bucket = []
                    copy = True
                elif itemize_elements and rawstring(line).startswith(items[1]):
                    # print('end')
                    processed_lines.append('')  # Extra blank
                    for bline in bucket:
                        # if it's not a blank line
                        if len(bline) != 0:
                            processedline = '- ' + bline
                            processed_lines.append(processedline)
                    processed_lines.append('')  # Extra blank

                    processedline = '## ' + line
                    processed_lines.append(processedline.upper())
                    copy = False
                    flagendinglist = True
                elif itemize_elements and copy:
                    # print('bucket')
                    bucket.append(line)
                else:
                    if flagendinglist and len(line) != 0:
                        # print('ending')
                        processedline = '- ' + line
                        processed_lines.append(processedline)
                    else:
                        if line.startswith('# '):
                            post_title = line
                            processed_lines.append(line)
                        elif not simplemarkup and len(line) <= 80 and len(line) >= 4 and not line.endswith('.') and not line.endswith('!') and not line.startswith('-'):
                            processedline = '## ' + line
                            processed_lines.append(processedline)
                        else:
                            processed_lines.append(line)
            post_output = '\n'.join(processed_lines)
            post_list.append(post_output)

            post_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow([post_title, markdown2.markdown(post_output.strip()), 'draft', post_date, random.choice(rand_categories), ''])

        text_file = open("output.txt", "w")
        text_file.write('&&&&!\n\n'.join(post_list))
        text_file.close()


if __name__ == "__main__":
    # This will only be executed when this module is run direcly
    from docopt import docopt
    main(docopt(__doc__))
