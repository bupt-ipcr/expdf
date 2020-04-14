#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-14 21:48
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
# arXiv.org
ARXIV_REGEX = r"""arxiv:\s?([^\s,]+)"""
ARXIV_REGEX2 = r"""arxiv.org/abs/([^\s,]+)"""

# DOI
DOI_REGEX = r"""DOI:\s?([^\s,]+)"""

# URL
URL_REGEX = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""


def extract_urls(text):
    return set(re.findall(URL_REGEX, text, re.IGNORECASE))


def extract_arxiv(text):
    res = re.findall(ARXIV_REGEX, text, re.IGNORECASE) + \
        re.findall(ARXIV_REGEX2, text, re.IGNORECASE)
    return set([r.strip(".") for r in res])


def extract_doi(text):
    res = set(re.findall(DOI_REGEX, text, re.IGNORECASE))
    return set([r.strip(".") for r in res])


def resolve_PDFObjRef(obj_ref, curpage):
    """
    Resolves PDFObjRef objects. Returns either None, a Reference object or
    a list of Reference objects.
    """
    if isinstance(obj_ref, list):
        return [resolve_PDFObjRef(item) for item in obj_ref]

    # print(">", obj_ref, type(obj_ref))
    if not isinstance(obj_ref, PDFObjRef):
        # print("type not of PDFObjRef")
        return None

    obj_resolved = obj_ref.resolve()
    # print("obj_resolved:", obj_resolved, type(obj_resolved))
    if isinstance(obj_resolved, bytes):
        obj_resolved = obj_resolved.decode("utf-8")

    if isinstance(obj_resolved, str):
        ref = obj_resolved
        return (ref, curpage)

    if isinstance(obj_resolved, list):
        return [resolve_PDFObjRef(o) for o in obj_resolved]

    if "URI" in obj_resolved:
        if isinstance(obj_resolved["URI"], PDFObjRef):
            return resolve_PDFObjRef(obj_resolved["URI"])

    if "A" in obj_resolved:
        if isinstance(obj_resolved["A"], PDFObjRef):
            return resolve_PDFObjRef(obj_resolved["A"])

        if "URI" in obj_resolved["A"]:
            # print("->", a["A"]["URI"])
            return (obj_resolved["A"]["URI"].decode("utf-8"),
                                curpage)
            

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