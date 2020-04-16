#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-16 17:15
@FilePath: /expdf/ref_resolve.py
@desc: 解析PDF中的

Web url matching:
* http://daringfireball.net/2010/07/improved_regex_for_matching_urls
* https://gist.github.com/gruber/889161
"""

from collections import namedtuple
from collections.abc import Iterable
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


def process_annots(annots):
    # 通过解析获取嵌套结果
    nesting_refs = resolve_PDFObjRef(annots)
    # 将结果平坦化
    flat_refs = flatten(nesting_refs)
    return flat_refs
    

def flatten(refs):
    """扁平化refs
    
    refs只能是Iterable或者是None
    当refs是None的时候，直接返回[]，否则迭代处理:
    循环获取refs中的元素
    - 若元素是Reference实例，则使用append方式添加到flatten_refs中
    - 若元素是Iterable，则调用flatten处理元素，处理结果是list，使用
      extend方式添加到fatten_refs中
    - 若不满足上述格式，则抛出异常
    完成之后返回flatten_refs
    
    @param refs: refs, list or None
    @return list, flatten refs
    """
    flatten_refs = []
    if refs is None:
        return flatten_refs
    for item in refs:
        if item is None:
            continue
        if isinstance(item, Reference):
            flatten_refs.append(item)
        elif isinstance(item, Iterable):
            item = flatten(item)
            flatten_refs.extend(list(item))
        else:
            raise TypeError(f"bad operand type for flatten(): '{type(refs)}'")
    return flatten_refs

if __name__ == '__main__':
    s1 = Reference(1, 'a')
    s2 = Reference(2, 'a')
    s3 = Reference(3, 'a')
    s4 = Reference(4, 'a')
    s5 = Reference(5, 'a')
    # l = [s1, [s2, [s3, [s4, None]]]]
    l = [s1, [s2, None]]
    # l = [s2, [s2, s3, s4], s5]
    r = flatten(l)
    print(r)