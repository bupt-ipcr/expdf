#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-05-06 11:16
@FilePath: /expdf/cli.py
@desc:
Command Line tool to get metadata, references and links from local ot remote PDFs,
and generate reference relation of all PDFs(given or inside PDF)
"""

import argparse
import expdf
from pathlib import Path
here = Path().resolve()


def create_parser():
    parser = argparse.ArgumentParser(
        prog="expdf",
        description="Generate reference relation of all PDFs(given or inside PDF)",
        epilog=""
    )

    parser.add_argument(
        '-a', type=str, metavar='APPEND_PDF', action='append',
        default=[],
        help="append a PDF file", dest='append_pdfs'
    )

    parser.add_argument(
        '-r', '--recursive', action='store_true',
        help="treat PDF_PATH as a directory"
    )

    parser.add_argument(
        'pdf_path', metavar='PDF_PATH',
        help="PDF path, or directory of PDFs if -r is used"
    )

    parser.add_argument(
        '-o', '-O', '--output', type=str, metavar='OUTPUT_DIR',
        help="output directory, default is current directory"
    )

    return parser


def command_line():
    parser = create_parser()
    args = parser.parse_args()

    pdfs = []
    pdf_path = here / args.pdf_path

    # glob all pdfs
    print(f'recursive is {args.recursive}')
    if args.recursive:
        print(f'find all pdf in {args.pdf_path}')
        for file in pdf_path.iterdir():
            print(f'find a file {file}')
            if file.suffix == '.pdf':
                pdfs.append(str(file))
    else:
        print(f'find pdf file at {args.pdf_path}')
        if pdf_path.suffix == '.pdf':
            pdfs.append(str(pdf_path))
        else:
            raise TypeError(f"{args.pdf_path} is not a pdf file")

    for append_pdf in args.append_pdfs:
        print(f'append a pdf file {append_pdf}')
        append_file = here / append_pdf
        if append_file.suffix == '.pdf':
            pdfs.append(str(append_file))
        else:
            raise TypeError(f"{append_file} is not a pdf file")

    # assert pdfs is not []
    if pdfs == []:
        print(f'no pdf file')

    print(f'generate expdf for pdf in pdfs')
    print(f'generate graph')
    print(f'generate svg html')


if __name__ == '__main__':
    command_line()
