#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-16 17:44
@FilePath: /expdf/utils.py
@desc: 

Web url matching:
* http://daringfireball.net/2010/07/improved_regex_for_matching_urls
* https://gist.github.com/gruber/889161
"""


from collections import namedtuple
from collections.abc import Iterable
from pdfminer.pdftypes import PDFObjRef
import re

Link = namedtuple('Link', 'uri, reftype')


def get_urls(text):
    """从text中匹配 urls
    @param text: 文本
    @return set, all urls
    """
    # URL
    URL_REGEX = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""
    return set(re.findall(URL_REGEX, text, re.IGNORECASE))


def get_arxivs(text):
    """从text中匹配 arxivs
    @param text: 文本
    @return set, all arxivs
    """
    ARXIV_REGEX = r"""arxiv:\s?([^\s,]+)"""
    ARXIV_REGEX2 = r"""arxiv.org/abs/([^\s,]+)"""
    res = re.findall(ARXIV_REGEX, text, re.IGNORECASE) + re.findall(ARXIV_REGEX2, text, re.IGNORECASE)
    return set([r.strip(".") for r in res])


def get_dois(text):
    """从text中匹配 dois
    @param text: 文本
    @return set, all dois
    """
    DOI_REGEX = r"""DOI:\s?([^\s,]+)"""
    res = set(re.findall(DOI_REGEX, text, re.IGNORECASE))
    return set([r.strip(".") for r in res])


def get_links(uri):
    """获取uri中包含的所有link
    在uri中依次检测资源类型，并添加到links中
    如果最终没有找到符合的资源类型，默认为url类型

    @param uri: 需要处理的资源
    @return: list link列表
    """
    links = []
    # 处理ref
    if uri.lower().endswith(".pdf"):
        links.append(Link(uri, 'pdf'))
    else:
        for arxiv_uri in get_arxivs(uri):
            links.append(Link(uri, 'pdf'))
        for doi_uri in get_dois(uri):
            links.append(Link(uri, 'pdf'))
    # 如果links中没有内容，则使用默认值
    if not links:
        links.append(Link(uri, 'url'))
    return links


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
