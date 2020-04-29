#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-29 20:22
@FilePath: /expdf/utils.py
@desc: 

Web url matching:
* http://daringfireball.net/2010/07/improved_regex_for_matching_urls
* https://gist.github.com/gruber/889161
"""


from collections.abc import Iterable
from pdfminer.pdftypes import PDFObjRef
from .extractor import (
    Link,
    get_links
)


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
        return get_links(obj_resolved)

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


def flatten(links):
    """扁平化links

    links只能是Iterable或者是None
    当links是None的时候，直接返回[]，否则迭代处理:
    循环获取links中的元素
    - 若元素是Link实例，则使用append方式添加到flatten_links中
    - 若元素是Iterable，则调用flatten处理元素，处理结果是list，使用
      extend方式添加到fatten_links中
    - 若不满足上述格式，则抛出异常
    完成之后返回flatten_links

    @param links: links, list or None
    @return list, flatten links
    """
    flatten_links = []
    if links is None:
        return flatten_links
    for item in links:
        if item is None:
            continue
        if isinstance(item, Link):
            flatten_links.append(item)
        elif isinstance(item, Iterable):
            item = flatten(item)
            flatten_links.extend(list(item))
        else:
            raise TypeError(f"bad operand type for flatten(): '{type(links)}'")
    return flatten_links
