#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-16 19:52
@FilePath: /expdf/processors.py
@desc: 
"""
from io import BytesIO
from pdfminer.layout import LAParams
from pdfminer.converter import TextConverter
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer import psparser
from pdfminer import settings as pdfminer_settings
import re
from .utils import Link
from .utils import flatten, resolve_PDFObjRef
from .utils import get_urls, get_arxivs, get_dois

pdfminer_settings.STRICT = False


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
    匹配text中的所有links
    匹配text中所有refs

    @param text: pdf 文本
    @return links, refs
    """
    # 处理links
    links = []
    links.extend(Link(url, 'url', url) for url in get_urls(text))
    links.extend(Link(arxiv, 'arxiv', f'http://arxiv.org/abs/{arxiv}') for arxiv in get_arxivs(text))
    # TODO: 增加DOI的link信息
    links.extend(Link(doi, 'doi') for doi in get_dois(text))

    # 处理refs
    refs = []
    lines = text.split('\n')
    # 找到REFERENCES位置
    ref_text = text[text.find('REFERENCES'):]
    ref_text = ref_text.replace('\n', '')
    ref_lines = re.findall(r'(?<=\[\d\]).*?“.+?”', ref_text)
    for ref_line in ref_lines:
        ref = re.search(r'(?<=“).+?(?=”)', ref_line)[0]
        refs.append(ref)
    return links, refs