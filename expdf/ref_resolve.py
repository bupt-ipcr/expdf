#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-14 21:57
@FilePath: /ref_resolve.py
@desc: 解析PDF中的

Web url matching:
* http://daringfireball.net/2010/07/improved_regex_for_matching_urls
* https://gist.github.com/gruber/889161
"""

from pdfminer.pdftypes import PDFObjRef
import re

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