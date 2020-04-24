#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-24 20:34
@FilePath: /expdf/processors.py
@desc: 
"""
from io import BytesIO
from pdfminer import settings as pdfminer_settings
pdfminer_settings.STRICT = False
from pdfminer.layout import LAParams
from pdfminer.converter import TextConverter
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdftypes import resolve1
from pdfminer import psparser
import re
from .utils import Link
from .utils import flatten, resolve_PDFObjRef
from .utils import get_urls, get_arxivs, get_dois
from .xmp import xmp_to_dict



def process_doc(doc: PDFDocument):
    """解析PDF文档对象

    旧版PDF将info存储在info字段中
    新版PDF在metadata中以XMP格式存储信息
    通过读取raw xmp数据，并转换为json格式返回

    @param doc: PDFDocument对象
    @return: 
        info: json格式的info信息，若没找到则返回{}
        metadata: json格式的metadata，若没找到则返回{}
    """
    # 如果info是列表，将其解析为json
    info = doc.info if doc.info else {}
    if isinstance(info, list):
        info = info[0]
    # 获取metadata
    if 'Metadata' in doc.catalog:
        # resolve1循环解析对象，直到被解析的对象不是PDFObjRef对象为止，相当于获取裸对象
        # resolve1(doc.catalog['Metadata']) 结果是PDFStream, get_data 获取裸数据
        metadata = resolve1(doc.catalog['Metadata']).get_data()
        # 使用xmp_to_dict函数解析XMP文档，获取metadata
        metadata = xmp_to_dict(metadata)
    else:
        metadata = {}
    return info, metadata


def process_annots(annots):
    """处理annots
    将annots解析为嵌套refs，再扁平化
    """
    # 通过解析获取嵌套结果
    nesting_links = resolve_PDFObjRef(annots)
    # 将结果平坦化
    flat_links = flatten(nesting_links)
    return flat_links


def process_pages(doc: PDFDocument):
    """按页处理doc文档
    将每页的信息通过 interpreter 处理到text_io中
    并且在处理每页信息的时候将注释信息处理

    @param doc: PDFDocument对象
    @return
        text: str 整个doc中的text信息
        annots_list: list 整个doc中的所有annots的列表
        maxpage: doc的最大页码
    """
    # 准备解析器
    text_io = BytesIO()
    rsrcmgr = PDFResourceManager(caching=True)
    converter = TextConverter(rsrcmgr, text_io, codec="utf-8",
                              laparams=LAParams(), imagewriter=None)
    interpreter = PDFPageInterpreter(rsrcmgr, converter)
    curpage = 0
    annots_list = []
    # 遍历page
    for page in PDFPage.create_pages(doc):
        # Read page contents
        interpreter.process_page(page)
        curpage += 1

        # Collect URL annotations
        # try:
        if page.annots:
            annots_list.append(page.annots)

    # Get text from stream
    text = text_io.getvalue().decode("utf-8")
    text_io.close()
    converter.close()
    maxpage = curpage
    return text, annots_list, maxpage


def process_text(text):
    """处理text

    匹配text中的所有links:
        分别使用url arxiv 和 doi 进行匹配，返回所有link的集合
    匹配text中所有refs:
        在text中找到 REFERENCES 的位置，在那之后的文本被视为引用页面
        在引用页面中匹配以 [n] 开头且包含 “xxx” 的文本
        将文本重新匹配，只保留“”内部的信息，并去除首末的标点

    @param text: pdf 文本
    @return links, refs
    """
    # 处理links
    links = []
    links.extend(Link(url, 'url', url) for url in get_urls(text))
    links.extend(Link(arxiv, 'arxiv', f'http://arxiv.org/abs/{arxiv}') for arxiv in get_arxivs(text))
    # TODO: 增加DOI的link信息
    links.extend(Link(doi, 'doi', doi) for doi in get_dois(text))

    # 处理refs
    refs = []
    lines = text.split('\n')
    # 找到REFERENCES位置
    ref_text = text[text.find('REFERENCES'):]
    # 将\n替换掉，以便re搜索
    ref_text = ref_text.replace('\n', '')
    # 查找[n]开头且包含 “” 的文本
    ref_lines = re.findall(r'(?<=\[\d\]).*?“.+?”', ref_text)
    for ref_line in ref_lines:
        # 匹配“”中的文本，因为之前匹配过一次，所以一定能search到结果，不需要判断
        ref = re.search(r'(?<=“).+?(?=”)', ref_line)[0]
        # 删除首末的标点
        ref = re.sub('[,，.。]$', '', ref)
        refs.append(ref)
    return links, refs
