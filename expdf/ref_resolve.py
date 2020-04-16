#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-16 16:34
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


def resolve_PDFObjRef(pdfobj):
    """处理PDF对象，递归查找所有引用并返回
    @param pdfobj: PDFObjRef 对象
    @return: list or nesting lists or None
    """
    if isinstance(pdfobj, list):
        return [resolve_PDFObjRef(item) for item in pdfobj]

    if not isinstance(pdfobj, PDFObjRef):
        return None

    # 如果是PDFObjRef，则将其resolve之后继续判断
    obj_resolved = pdfobj.resolve()
    
    # 优先进行短路判断
    if isinstance(obj_resolved, str):
        return get_refs(obj_resolved)
    
    # bytes: decode
    if isinstance(obj_resolved, bytes):
        obj_resolved = obj_resolved.decode("utf-8")

    # list: recursive resolve
    if isinstance(obj_resolved, list):
        return [resolve_PDFObjRef(o) for o in obj_resolved]

    # process resource
    if "URI" in obj_resolved:
        if isinstance(obj_resolved["URI"], PDFObjRef):
            return resolve_PDFObjRef(obj_resolved["URI"])

    if "A" in obj_resolved:
        if isinstance(obj_resolved["A"], PDFObjRef):
            return resolve_PDFObjRef(obj_resolved["A"])

