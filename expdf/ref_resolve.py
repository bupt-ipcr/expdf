#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-16 16:23
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

def get_refs(uri):
    """获取uri中包含的所有ref
    在uri中依次检测资源类型，并添加到refs中
    如果最终没有找到符合的资源类型，默认为url类型
    
    @param uri: 需要处理的资源
    @return: list ref列表
    """
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
    return refs

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
