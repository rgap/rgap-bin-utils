#!/usr/bin/env python3
"""This converts a jupyter notebook into latex and then into a pdf file.

Usage:
    rgap_jupyter2pdf.py <input_file> <citations_file>
    rgap_jupyter2pdf.py <input_file>

    rgap_jupyter2pdf.py -h

Arguments:
    input_file       input "ipynb" file
    citations_file   citations "bib" file

"""


import os


def main(args):
    input_file = args["<input_file>"]
    citations_file = args["<citations_file>"]

    file_content = (
        ("((*- extends 'article.tplx' -*))\n\n")
        + ("((* block author *))\n")
        + ("\\author{Rel Guzman}\n")
        + ("((* endblock author *))\n\n")
        + ("((* block bibliography *))\n")
        + ("\\bibliographystyle{plain}\n")
        + ("\\bibliography{{{}}}\n").format(os.path.splitext(citations_file)[0])
        + ("((* endblock bibliography *))\n")
    )

    f = open("citations.tplx", "w")
    f.write(file_content)
    f.close()

    input_file_name = os.path.splitext(input_file)[0]

    if not citations_file:
        os.system("jupyter nbconvert " + input_file_name + " --to latex")
    else:
        os.system(
            "jupyter nbconvert "
            + input_file_name
            + " --to latex --template citations.tplx"
        )

    os.system("latex -interaction nonstopmode " + input_file_name + ".tex")
    os.system("bibtex " + input_file_name + ".aux")
    os.system("pdflatex " + input_file_name + ".tex")
    os.system("pdflatex " + input_file_name + ".tex")


if __name__ == "__main__":
    # This will only be executed when this module is run direcly
    from docopt import docopt

    main(docopt(__doc__))
