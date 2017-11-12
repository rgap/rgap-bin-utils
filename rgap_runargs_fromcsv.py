#!/usr/bin/env python3
"""This can run another script with arguments from a csv file.

Usage:
    rgap_runargs_fromcsv.py <csv_input> <script_file> <arguments> [--prefix=<prefix>]

    rgap_runargs_fromcsv.py -h

Arguments:
    csv_input      csv file
    script_file    path to the script file to run
    arguments      arguments e.g. "link,a <text> src mp3 <href,src>". The ones in brackets is a column in the csv file.
    prefix         prefix to put to the files

Examples:
    rgap_runargs_fromcsv.py urls.csv rgap_getfiles.py "embed,link,a,audio,source href,src wav,mp3,wma,m4a,ogg <href> --prefix=" --prefix=discussion

"""

from selenium import webdriver
from urllib.parse import urlparse
from urllib.error import HTTPError, URLError
from pyjsparser import PyJsParser
import os
import os.path
from lxml import html
import csv
# import json


def main(args):

    csv_input = args['<csv_input>']
    script_file = args['<script_file>']
    arguments = args['<arguments>']
    prefix = args['--prefix']

    arguments = arguments.split(' ')
    argument_list = []
    for arg in arguments:
        if arg[0] == '<':
            arg = arg[arg.find("<")+1:arg.find(">")].split(',')
        argument_list.append(arg)

    # print(argument_list)

    with open(csv_input, "r") as csv_file:
        reader = csv.DictReader(csv_file)
        for row_index, row in enumerate(reader, start=1):
            command_arguments = ''
            for args in argument_list:
                if isinstance(args, list):
                    values = ''
                    for index, csv_column in enumerate(args):
                        values += row[csv_column]
                        if not index == len(args)-1:
                            values += ','
                    command_arguments += values
                else:
                    if args.startswith('--prefix='):
                        if prefix is not None:
                            command_arguments += '--prefix=' + str(row_index) + '_' + prefix
                    else:
                        command_arguments += args
                command_arguments += ' '

            command = (script_file + " %s") % (command_arguments)
            print(command)
            # Run command
            try:
                os.system(command)
            except:
                print("error running command")
                raise

if __name__ == "__main__":
    # This will only be executed when this module is run direcly
    from docopt import docopt
    main(docopt(__doc__))
