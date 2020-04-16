#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-16 17:40
@FilePath: /expdf/xxpdf.py
@desc: 
"""
from io import BytesIO
import json
from pathlib import Path
from pdfminer.pdftypes import resolve1
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer import settings as pdfminer_settings
from pprint import pprint
import re
import requests
from .processors import process_annots, process_pages, process_text
from .utils import Reference
from .utils import get_urls, get_arxivs, get_dois
from .xmp import xmp_to_dict

pdfminer_settings.STRICT = False


def get_stream(uri, local=False):
    """将给定uri转换为stream

    在uri中查找url
    如果强制使用本地文件，或者没找到url，则尝试在本地打开文件
    若在本地找不到文件则报错，否则将文件打开为stream

    如果不强制且找到了url，则向网络请求，返回数据转为stream

    @param uri: 资源链接
    @param local: 是否强制在本地查找 default False

    @return: stream, filename
    """
    # 尝试在uri中查找url
    urls = get_urls(uri)
    local = local or not urls

    if local:
        path = Path(uri)
        if not path.exists():
            raise FileNotFoundError(f"Invalid local filename: {uri}")
        else:
            filename, stream = path.name, path.open("rb")
    else:
        content = requests.get(uri).content
        filename, stream = uri.split("/")[-1], BytesIO(content)

    return filename, stream


def get_info(doc: PDFDocument):
    """从文档中获取info
    旧版PDF将info存储在info字段中   

    @param doc: PDFDocument对象
    @return: doc中的info信息
    """
    return doc.info


def get_metadata(doc: PDFDocument):
    """从文档中解析metadata
    新版PDF在metadata中以XMP格式存储信息
    通过读取raw xmp数据，并转换为json格式返回

    @param doc: PDFDocument对象
    @return: json格式的metadata，若没找到则返回{}
    """
    if 'Metadata' in doc.catalog:
        # resolve1循环解析对象，直到被解析的对象不是PDFObjRef对象为止，相当于获取裸对象
        # resolve1(doc.catalog['Metadata']) 结果是PDFStream, get_data 获取裸数据
        metadata = resolve1(doc.catalog['Metadata']).get_data()
        # 使用xmp_to_dict函数解析XMP文档，获取metadata
        metadata = xmp_to_dict(metadata)
    else:
        metadata = {}
    return metadata


def resolve_pdf(uri='tests/test.pdf', password='', pagenos=[], maxpages=0):
    # 将PDF文件打开为stream
    fname, pdf_stream = get_stream(uri)

    # 使用PDFMiner解析stram内容
    parser = PDFParser(pdf_stream)
    doc = PDFDocument(parser, password=password, caching=True)

    # 获取info
    info = get_info(doc)
    # 获取metadata（如果有）
    metadata = get_metadata(doc)
    
    # 获取pdf text信息和annots列表
    text, annots_list, maxpage = process_pages(doc)

    references = []
    for annots in annots_list:
        annots_refs = process_annots(annots)
        if annots_refs:
            references.extend(annots_refs)

    # Extract URL references from text
    text_refs = process_text(text)
    references.extend(text_refs)

    pdf_json = {
        'text': text,
        'metadata': metadata,
        'references': references
    }
    return pdf_json


if __name__ == '__main__':
    pdf = resolve_pdf()
    pprint(pdf['metadata'])
    pprint(pdf['references'])
