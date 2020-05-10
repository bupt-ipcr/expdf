#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-05-10 10:47
@FilePath: /expdf/expdf/cli.py
@desc:
Command Line tool to get metadata, references and links from local ot remote PDFs,
and generate reference relation of all PDFs(given or inside PDF)
"""

import argparse
from expdf import (
    LocalPDFNode,
    ExPDFParser,
    render
)
from expdf.graph import PDFNode
import json
import logging
from pathlib import Path
from tqdm import tqdm
import sys

here = Path().resolve()
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


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
        help="output directory, default is current directory",
        default='data.json'
    )

    return parser


def command_line():
    parser = create_parser()
    args = parser.parse_args()

    pdfs = []
    pdf_path = here / args.pdf_path

    # glob all pdfs
    logger.info(f'recursive is {args.recursive}')
    if args.recursive:
        logger.info(f'find all pdf in {args.pdf_path}')
        for file in pdf_path.iterdir():
            logger.info(f'  find a file {file}')
            if file.suffix == '.pdf':
                logger.info(f'  append a pdf file {file}')
                pdfs.append(file)
    else:
        logger.info(f'find pdf file at {args.pdf_path}')
        if pdf_path.suffix == '.pdf':
            pdfs.append(pdf_path)
        else:
            msg = f"{parser.prog}: error: {args.pdf_path} is not a pdf file"
            print(msg, file=sys.stderr)
            sys.exit(2)

    # get all append pdfs
    for append_pdf in args.append_pdfs:
        logger.info(f'append a pdf file {append_pdf}')
        append_file = here / append_pdf
        if append_file.suffix == '.pdf':
            pdfs.append(append_file)
        else:
            msg = f"{parser.prog}: error: {append_file} is not a pdf file"
            print(msg, file=sys.stderr)
            sys.exit(2)

    # assert pdfs is not []
    if pdfs == []:
        logger.warning(f'no pdf file')

    for pdf in tqdm(pdfs, desc="parser all pdfs"):
        if not pdf.exists():
            raise FileNotFoundError(f"No such file or directory: '{pdf}'")
        else:
            logger.info(f'create LocalPDFNode of {pdf}')
            expdf_parser = ExPDFParser(f"{pdf.resolve()}")
            localPDFNode = LocalPDFNode(expdf_parser.title, expdf_parser.refs)

    pdf_info = PDFNode.get_json()
    with open(args.output, 'w') as f:
        f.write(pdf_info)


if __name__ == '__main__':
    command_line()
