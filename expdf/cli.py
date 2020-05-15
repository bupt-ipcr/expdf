#!/usr/bin/env python
# coding=utf-8
"""
Command Line tool to get metadata, references and links from local ot remote 
PDFs, and generate reference relation of all PDFs(given or inside PDF)

@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-05-15 15:29
@FilePath: /expdf/expdf/cli.py
"""

import argparse
from expdf import (
    LocalPDFNode,
    PDFNode,
    ExPDFParser,
    render
)
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
        '-a', '--append', type=str, default=[],
        metavar='APPEND_PDF', action='append',
        help="append a PDF file", dest='append_pdfs'
    )

    parser.add_argument(
        '-d', '--dir', '--directory', action='store_true',
        help="treat PDF_PATH as a directory",
        dest='directory'
    )

    parser.add_argument(
        '-e', '--exclude', type=str, default=[],
        metavar='EXCLUDE_PDF', action='append',
        help="exclude a PDF file", dest='exclude_pdfs'
    )

    parser.add_argument(
        '-o', '-O', '--output', type=str, metavar='OUTPUT_DIR',
        help="output directory, default is current directory",
        default='data.json'
    )

    parser.add_argument(
        'pdf_path', metavar='PDF_PATH',
        help="PDF path, or directory of PDFs if -r is used"
    )

    parser.add_argument(
        '-v', '--vis', '--visualize', action='store_true',
        help="create a html file for visualize",
        dest='visualize'
    )

    parser.add_argument(
        '--vis-html', metavar='HTML_FILENAME',
        help="output file name of html visualize",
        default='relations.html'
    )

    return parser


def get_pdfs(parser, args):
    """Get list of path of PDFs allocated from argument parser.

    Get path of PDF with parameter `PDF_PATH`, or get all path of PDFs
    in `PDF_PATH` if `-r` is specified. Then check list of `APPEND_PDF`
    specified by `-a`, and exclude all PDFs in list of `EXCLUDE_PDF`
    specified by `-e`.

    Any of the path is subscribed by a instance of `pathlib.Path`.

    Parameters
    ----------
    parser : instance of :class:`argparse.ArgumentParser`, contains
        parser infomations.
    args : parser.parse_args(), all args get from command line.

    Returns
    -------
    PDFs : list of instance of :class: `pathlib.Path`
    """
    pdfs = []
    pdf_path = here / args.pdf_path
    # glob all pdfs
    logger.info(f'treat as directory is {args.directory}')
    if args.directory:
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

    # exclude all pdfs, no error even exclude file not exists
    for exclude_pdf in args.exclude_pdfs:
        logger.info(f'exclude a pdf file {exclude_pdf}')
        exlcude_file = here / exclude_pdf
        if exclude_pdf in pdfs:
            pdfs.remove(exclude_pdf)

    # assert pdfs is not []
    if pdfs == []:
        logger.warning(f'no pdf file')

    return pdfs


def command_line():
    """Command line entry of expdf."""
    parser = create_parser()
    args = parser.parse_args()
    logging.info(args)

    pdfs = get_pdfs(parser, args)
    logging.info(pdfs)

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

    if args.visualize:
        pdf_json = json.loads(pdf_info)
        render(pdf_json, args.vis_html)


if __name__ == '__main__':
    command_line()
