#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-13 10:42
@FilePath: /test.py
@desc: 
"""


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

class PDFMinerBackend(ReaderBackend):
    def __init__(self, pdf_stream, password='', pagenos=[], maxpages=0):
        self.pdf_stream = pdf_stream

        # Extract Metadata
        parser = PDFParser(pdf_stream)
        doc = PDFDocument(parser, password=password, caching=True)
        if doc.info:
            for k in doc.info[0]:
                v = doc.info[0][k]
                # print(repr(v), type(v))
                if isinstance(v, (bytes, str, unicode)):
                    self.metadata[k] = make_compat_str(v)
                elif isinstance(v, (psparser.PSLiteral, psparser.PSKeyword)):
                    self.metadata[k] = make_compat_str(v.name)

        # Secret Metadata
        if 'Metadata' in doc.catalog:
            metadata = resolve1(doc.catalog['Metadata']).get_data()
            # print(metadata)  # The raw XMP metadata
            # print(xmp_to_dict(metadata))
            self.metadata.update(xmp_to_dict(metadata))
            # print("---")

        # Extract Content
        text_io = BytesIO()
        rsrcmgr = PDFResourceManager(caching=True)
        converter = TextConverter(rsrcmgr, text_io, codec="utf-8",
                                  laparams=LAParams(), imagewriter=None)
        interpreter = PDFPageInterpreter(rsrcmgr, converter)

        self.metadata["Pages"] = 0
        self.curpage = 0
        for page in PDFPage.get_pages(self.pdf_stream, pagenos=pagenos,maxpages=maxpages, password=password,caching=True, check_extractable=False):
            # Read page contents
            interpreter.process_page(page)
            self.metadata["Pages"] += 1
            self.curpage += 1

            # Collect URL annotations
            # try:
            if page.annots:
                refs = self.resolve_PDFObjRef(page.annots)
                if refs:
                    if isinstance(refs, list):
                        for ref in refs:
                            if ref:
                                self.references.add(ref)
                    elif isinstance(refs, Reference):
                        self.references.add(refs)

            # except Exception as e:
                # logger.warning(str(e))

        # Remove empty metadata entries
        self.metadata_cleanup()

        # Get text from stream
        self.text = text_io.getvalue().decode("utf-8")
        text_io.close()
        converter.close()
        # print(self.text)

        # Extract URL references from text
        for url in extractor.extract_urls(self.text):
            self.references.add(Reference(url, self.curpage))

        for ref in extractor.extract_arxiv(self.text):
            self.references.add(Reference(ref, self.curpage))

        for ref in extractor.extract_doi(self.text):
            self.references.add(Reference(ref, self.curpage))