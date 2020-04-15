#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-15 23:45
@FilePath: /expdf/ref_resolve.py
@desc: 解析PDF中的

Web url matching:
* http://daringfireball.net/2010/07/improved_regex_for_matching_urls
* https://gist.github.com/gruber/889161
"""

from collections import namedtuple
from pdfminer.pdftypes import PDFObjRef
import re
from utils import get_urls, get_arxivs, get_dois

Reference = namedtuple('Reference', 'uri, reftype')


class References:
    """ Generic Reference """

    def __init__(self, uri):
        refs = []

        # 处理ref
        if uri.lower().endswith(".pdf"):
            refs.append(Reference(uri, 'pdf'))
        else:
            for arxiv_uri in get_arxivs(uri):
                refs.append(Reference(uri, 'pdf'))
            for doi_uri in get_dois(uri):
                refs.append(Reference(uri, 'pdf'))
        # 如果refs中没有内容，则使用默认值
        if not refs:
            refs.append(Reference(uri, 'url'))

    @classmethod
    def from_refs(cls, refs):
        """从一组Reference创建References的构造函数"""
        self.refs = refs.copy()

    @property
    def data(self):
        return self.refs

    def __add__(self, other):
        """满足References之间的加法"""
        if isinstance(other, References):
            refs = self.data.copy()
            refs.extend(other.data.copy())
            return References.from_refs(refs)
        else:
            raise TypeError("only support operand type(s) for +: 'References' and 'References'")


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
        return References(obj_resolved)

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
            return References(obj_resolved["A"]["URI"].decode("utf-8"))
