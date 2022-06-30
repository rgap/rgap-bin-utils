#!/usr/bin/env python3
"""Get TOC from a pdf file

Usage:
    .py <input> <output>

    .py -h

Arguments:
	input       input
	output      output

"""


import os
import fitz
import time


def main(args):

	input_file = args['<input>']
	output_file = args['<output>']

	# doc = fitz.open(input_file)
	# toc = doc.get_toc()
	# print(toc)

	tmp_output = 'tmp_toc.txt'

	command = ("mutool show '%s' outline > '%s'") % (input_file, tmp_output)


	try:
		os.system(command)

		# output toc file
		out = open(output_file, 'w')

		while not os.path.exists(tmp_output):
			time.sleep(1)
		if os.path.isfile(tmp_output):
		    f = open(tmp_output, 'r')
		    lines = f.readlines()
		    os.remove(tmp_output)
		    for line in lines:
		    	# print(line.split("#page", 1)[0])
		    	out.write(line.split("#page", 1)[0] + '\n')

		else:
		    raise ValueError("%s isn't a file!" % tmp_output)

	except:
		print("error running")
		raise


if __name__ == "__main__":
    # This will only be executed when this module is run direcly
    from docopt import docopt
    main(docopt(__doc__))
