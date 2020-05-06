#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-05-06 21:41
@FilePath: /expdf/processors.py
@desc: 处理器集合
"""
from pdfminer import settings as pdfminer_settings
pdfminer_settings.STRICT = False

from io import BytesIO
from pdfminer.layout import LAParams
from pdfminer.converter import TextConverter
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdftypes import resolve1
import re
from .extractor import (
    Link,
    get_ref_title,
    get_links
)
from .utils import flatten, resolve_PDFObjRef
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


def process_text(text, force_strict=False):
    """处理text

    匹配text中的所有links:
        分别使用url arxiv 和 doi 进行匹配，返回所有link的集合
    匹配text中所有refs:
        在text中找到 REFERENCES 的位置，在那之后的文本被视为引用页面
        在引用页面中匹配以 [n] 开头且包含 “xxx” 的文本
        将文本重新匹配，只保留“”内部的信息，并去除首末的标点

    Args:
        text (str): pdf 文本
        force_strict (bool): 强制启用strict模式
        
    Returns:
        list: text中查找到的links
        list: text中查找到的refs
    """
    # 处理links
    links = get_links(text)

    # 处理refs
    refs = []
    # get start of “References”
    if re.search(r'\sREFERENCES\s', text, re.I):        # usually it's surrounded by \s
        ref_start = re.search(r'\sREFERENCES\s', text, re.I).span()[1]
    elif re.search(r'REFERENCES\s|\sREFERENCES', text, re.I): 
        ref_start = re.search(r'REFERENCES\s|\sREFERENCES', text, re.I).span()[1]
    elif re.search(r'REFERENCES', text, re.I): 
        ref_start = re.search(r'REFERENCES', text, re.I).span()[1]
    else:
        return links, []

    ref_text = text[ref_start:]
    
    # 使用各种论文引用格式匹配ref标题，匹配不到的暂时使用ref全文作为标题

    # 如果在ref_text的前10个字符中搜索到 [1] 形式的 引用序号，则用 [\d+] 作为分隔符
    if re.search(r'\[\d+\]', ref_text[:10]):
        ref_text = ref_text.replace('\n', ' ')   # 将\n替换掉，以便re搜索
        ref_lines = re.split(r'\[\d+\]', ref_text)  # 用[\d+]分割
        for ref_line in ref_lines:
            if not ref_line:
                continue
            ref_line = ref_line.strip()  # 删除文本前后的空白字符
            ref = get_ref_title(ref_line, strict=force_strict)   # 获取引用文章的标题
            if ref:
                refs.append(ref)
    # 否则用\n\n分割，且在匹配时采用严格模式
    else:
        ref_lines = re.split(r'(?<=[^A-Z]\.)\s*?\n{1,2}[^a-zA-Z]*?(?=[A-Z])', ref_text, 0, re.U)
        for ref_line in ref_lines:
            ref_line = ref_line.replace('\n', ' ')   # 将\n替换掉，以便re搜索
            ref_line = ref_line.strip()  # 删除文本前后的空白字符
            if not ref_line:
                continue
            ref = get_ref_title(ref_line, strict=True)
            if ref:
                refs.append(ref)
                
    return links, refs
