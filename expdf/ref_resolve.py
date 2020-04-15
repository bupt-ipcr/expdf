#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-15 17:55
@FilePath: /expdf/ref_resolve.py
@desc: 解析PDF中的

Web url matching:
* http://daringfireball.net/2010/07/improved_regex_for_matching_urls
* https://gist.github.com/gruber/889161
"""

from pdfminer.pdftypes import PDFObjRef
import re
from .utils import get_urls, get_arxivs, get_dois


class Reference:
    """ Generic Reference """
    def __init__(self, uri, page=0):
        self.ref = uri
        self.reftype = "url"
        self.page = page

        # Detect reftype by filetype
        if uri.lower().endswith(".pdf"):
            self.reftype = "pdf"
            return

        # Detect reftype by extractor
        arxivs = get_arxivs(uri)
        if arxivs:
            self.ref = arxivs.pop()
            self.reftype = "arxiv"
            return

        dois = get_dois(uri)
        if dois:
            self.ref = dois.pop()
            self.reftype = "doi"
            return

    def __hash__(self):
        return hash(self.ref)

    def __eq__(self, other):
        assert isinstance(other, Reference)
        return self.ref == other.ref

    def __str__(self):
        return "<%s: %s>" % (self.reftype, self.ref)


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
        return Reference(ref, curpage)

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
            return Reference(obj_resolved["A"]["URI"].decode("utf-8"), curpage)
