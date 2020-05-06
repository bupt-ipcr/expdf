#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-05-06 16:42
@FilePath: /expdf/cli.py
@desc:
Command Line tool to get metadata, references and links from local ot remote PDFs,
and generate reference relation of all PDFs(given or inside PDF)
"""

import argparse
from expdf import (
    LocalPDFNode,
    Graph,
    ExPDFParser,
    render
)
import logging
from pathlib import Path
from tqdm import tqdm
import sys

here = Path().resolve()
logging.basicConfig(level=logging.WARNING)


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


def graph_all(pdfs):
    logging.info(f'generate expdf for pdf in pdfs')
    for pdf in tqdm(pdfs, desc="parser all pdfs"):
        if not pdf.exists():
            raise FileNotFoundError(f"No such file or directory: '{pdf}'")
        else:
            logging.info(f'create LocalPDFNode of {pdf}')
            expdf_parser = ExPDFParser(f"{pdf.resolve()}")
            localPDFNode = LocalPDFNode(expdf_parser.title, expdf_parser.refs)

    logging.info(f'generate graph')
    graph = Graph()
    graph.calculate()

    logging.info(f'generate svg html')
    render(graph.infos, 'svg.html')


def command_line():
    parser = create_parser()
    args = parser.parse_args()

    pdfs = []
    pdf_path = here / args.pdf_path

    # glob all pdfs
    logging.info(f'recursive is {args.recursive}')
    if args.recursive:
        logging.info(f'find all pdf in {args.pdf_path}')
        for file in pdf_path.iterdir():
            logging.info(f'  find a file {file}')
            if file.suffix == '.pdf':
                logging.info(f'  append a pdf file {file}')
                pdfs.append(file)
    else:
        logging.info(f'find pdf file at {args.pdf_path}')
        if pdf_path.suffix == '.pdf':
            pdfs.append(pdf_path)
        else:
            msg = f"{parser.prog}: error: {args.pdf_path} is not a pdf file"
            print(msg, file=sys.stderr)
            sys.exit(2)

    # get all append pdfs
    for append_pdf in args.append_pdfs:
        logging.info(f'append a pdf file {append_pdf}')
        append_file = here / append_pdf
        if append_file.suffix == '.pdf':
            pdfs.append(append_file)
        else:
            msg = f"{parser.prog}: error: {append_file} is not a pdf file"
            print(msg, file=sys.stderr)
            sys.exit(2)

    # assert pdfs is not []
    if pdfs == []:
        logging.warning(f'no pdf file')

    if pdfs:
        graph_all(pdfs)


if __name__ == '__main__':
    command_line()
