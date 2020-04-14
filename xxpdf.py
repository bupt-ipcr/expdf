#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-14 21:55
@FilePath: /xxpdf.py
@desc: 
"""
from pprint import pprint
import json
from pdfminer import settings as pdfminer_settings
pdfminer_settings.STRICT = False
from pdfminer import psparser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdftypes import resolve1, PDFObjRef
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from io import BytesIO
from xmp import xmp_to_dict
import re

from ref_resolve import resolve_PDFObjRef
            

def resolve_pdf(uri='test.pdf', password='', pagenos=[], maxpages=0):    
    password, pagenos, maxpages = '', [], 0

    pdf_stream = open(uri, "rb")
    parser = PDFParser(pdf_stream)
    doc = PDFDocument(parser, password=password, caching=True)

    # Secret Metadata
    if 'Metadata' in doc.catalog:
        metadata = resolve1(doc.catalog['Metadata']).get_data()

    # Extract Content
    text_io = BytesIO()
    rsrcmgr = PDFResourceManager(caching=True)
    converter = TextConverter(rsrcmgr, text_io, codec="utf-8",
                                laparams=LAParams(), imagewriter=None)
    interpreter = PDFPageInterpreter(rsrcmgr, converter)
    metadata = xmp_to_dict(metadata)
    metadata["Pages"] = 0
    curpage = 0

    references = []
    for page in PDFPage.get_pages(pdf_stream, pagenos=pagenos,
                                    maxpages=maxpages, password=password,
                                    caching=True, check_extractable=False):
        # Read page contents
        interpreter.process_page(page)
        metadata["Pages"] += 1
        curpage += 1

        # Collect URL annotations
        # try:
        if page.annots:
            refs = resolve_PDFObjRef(page.annots, curpage)
            if refs:
                if isinstance(refs, list):
                    for ref in refs:
                        if ref:
                            references.append(ref)
                references.append(refs)

        # except Exception as e:
            # logger.warning(str(e))


    # Get text from stream
    text = text_io.getvalue().decode("utf-8")
    text_io.close()
    converter.close()
    # print(text)

    # Extract URL references from text
    for url in extract_urls(text):
        references.append((url, curpage))

    for ref in extract_arxiv(text):
        references.append((ref, curpage))

    for ref in extract_doi(text):
        references.append((ref, curpage))
        
    pdf_json = {
        'metadata': metadata,
        'references': references
    }
    return pdf_json

if __name__ == '__main__':
    metadata, references = resolve_pdf().values()
    pprint(metadata)
    pprint(references)