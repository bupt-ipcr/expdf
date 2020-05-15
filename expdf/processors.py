#!/usr/bin/env python
# coding=utf-8
"""
Processers for resolve PDF.

@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-05-15 20:18
@FilePath: /expdf/expdf/processors.py
"""
from .xmp import xmp_to_dict
from .utils import flatten, resolve_PDFObjRef
from .extractor import (
    Link,
    get_ref_title,
    get_links
)
import re
from pdfminer.pdftypes import resolve1
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdocument import PDFDocument
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from io import BytesIO
from pdfminer import settings as pdfminer_settings
pdfminer_settings.STRICT = False


def process_doc(doc: PDFDocument):
    """Process PDF Document, return info and metadata.

    Some PDF store infomations such as title in field info,
    some newer PDF sotre them in field metadata. The
    processor read raw XMP data and convert to dictionary.

    Parameters
    ----------
    doc : PDFDocument
        PDF Document object to process.

    Returns
    -------
    info : dict
        Field info of the doc, return {} if no info field.
    metadata : dict
        Field metadata of the doc, return {} if no metadata field.
    """
    # if info is a list, resolve it
    info = doc.info if doc.info else {}
    if isinstance(info, list):
        info = info[0]
    # try to get metadata
    if 'Metadata' in doc.catalog:
        # resolve1 will resolve object recursively
        # result of resolve1(doc.catalog['Metadata']) is PDFStream
        metadata = resolve1(doc.catalog['Metadata']).get_data()
        # use xmp_to_dict to resolve XMP and get metadata
        metadata = xmp_to_dict(metadata)
    else:
        metadata = {}
    return info, metadata


def process_annots(annots):
    """Process annotates, return list of Link.
    
    Links in annotates will be resolved recursively,
    and the result will be flatten to a 1-dim list.

    Parameters
    ----------
    annots : a PDF object taht contains annotate(s)

    Returns
    -------
    flat_links : list of Link instance
    """
    # resolve nesting result of links
    nesting_links = resolve_PDFObjRef(annots)
    # flatten links
    flat_links = flatten(nesting_links)
    return flat_links


def process_pages(doc: PDFDocument):
    """Process document by page.

    Use an interpreter to process pages, extract text
    and annotates. Text will be put into a bytes io
    and then convert into string; annotates will record
    in a list; max page number will be found in process.

    Parameters
    ----------
    doc : PDFDocument
        PDF document to be processed.

    Returns
    -------
    text : str 
        text infomations of the complete PDF.
    annots_list : list
        a list of annotates in the PDF annots.
    maxpage : int
        max page number of PDF.
    """
    # prepare parser
    text_io = BytesIO()
    rsrcmgr = PDFResourceManager(caching=True)
    converter = TextConverter(rsrcmgr, text_io, codec="utf-8",
                              laparams=LAParams(), imagewriter=None)
    interpreter = PDFPageInterpreter(rsrcmgr, converter)
    curpage = 0
    annots_list = []
    # traverse pages
    for page in PDFPage.create_pages(doc):
        # Read page contents
        interpreter.process_page(page)
        curpage += 1

        # Collect URL annotations
        # try:
        if page.annots:
            annots_list.append(page.annots)

    # Get text from stream
    text = text_io.getvalue().decode("utf-8")
    text_io.close()
    converter.close()
    maxpage = curpage
    return text, annots_list, maxpage


def process_text(text, force_strict=False):
    """Process text of PDF, get links and refs.


    Extract all doi, arxiv and url links from the text. When extract
    url-type links, each link will be check to ensure no repeat links.

    Find statement `References` from text to determine part of citations.
    In the part, try to seperate text to lines and extract title of cited
    paper in each line.

    Parameters
    ----------
    text : str
        text content of PDF file.
    force_strict : bool, default False
        Set to True to enable strict mode. In strict mode, line match none
        of regexs returns None.

    Returns
    -------
        links : list
            list of Link find in text
        refs : list
            list of title of citations in text
    """
    # extract links
    links = get_links(text)

    # extract refs
    refs = []
    # get start of “References”
    if re.search(r'\sREFERENCES\s', text, re.I):        # usually it's surrounded by \s
        ref_start = re.search(r'\sREFERENCES\s', text, re.I).span()[1]
    elif re.search(r'REFERENCES\s|\sREFERENCES', text, re.I):
        ref_start = re.search(r'REFERENCES\s|\sREFERENCES',
                              text, re.I).span()[1]
    elif re.search(r'REFERENCES', text, re.I):
        ref_start = re.search(r'REFERENCES', text, re.I).span()[1]
    else:
        return links, []

    ref_text = text[ref_start:]

    # if [1]-type statement can be found after `References` statement,
    # use [\d+] as seperater
    if re.search(r'\[\d+\]', ref_text[:10]):
        ref_text = ref_text.replace('\n', ' ')   # replace \n as '' for regex search
        ref_lines = re.split(r'\[\d+\]', ref_text)  # use [\d] as seperater
        for ref_line in ref_lines:
            if not ref_line:
                continue
            ref_line = ref_line.strip()  # remove blank chars
            ref = get_ref_title(ref_line, strict=force_strict)   # get title of citation
            if ref:
                refs.append(ref)
    # elsewise use \n\n as seperater, and use strict 
    else:
        ref_lines = re.split(
            r'(?<=[^A-Z]\.)\s*?\n{1,2}[^a-zA-Z]*?(?=[A-Z])', ref_text, 0, re.U)
        for ref_line in ref_lines:
            ref_line = ref_line.replace('\n', ' ')   # replace \n as '' for regex search
            ref_line = ref_line.strip()  # remove blank chars
            if not ref_line:
                continue
            ref = get_ref_title(ref_line, strict=True)
            if ref:
                refs.append(ref)

    return links, refs
