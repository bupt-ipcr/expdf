#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-16 22:20
@FilePath: /expdf/parser.py
@desc: 
"""
from io import BytesIO
import json
from pathlib import Path

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer import settings as pdfminer_settings
from pprint import pprint
import re
import requests
from .processors import *
from .utils import Link
from .utils import get_urls, get_arxivs, get_dois

pdfminer_settings.STRICT = False


class ExPDF:
    """解析后的PDF对象"""

    def __init__(self, uri, local=False):
        filename, stream = get_stream(uri)
        expdf = expdf_parser(stream)
        expdf.update({
            'filename': filename
        })
        self.expdf = expdf

    @property
    def title(self):
        info, metadata = self.expdf['info'], self.expdf['metadata']
        # 尝试从info中恢复title
        if 'Title' in info:
            title = info['Title']
            if isinstance(title, bytes):
                return title.decode('utf-8')
            else:
                return title
        # 如果失败，尝试从metadata获取
        if 'dc' in metadata:
            if 'title' in metadata['dc']:
                return metadata['dc']['title']['x-default']
        # 如果找不到title，则抛出异常
        raise AttributeError("has no attribute 'title'")


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


def expdf_parser(pdf_stream, password='', pagenos=[], maxpages=0):
    """解析pdf stream"""

    # 使用PDFMiner解析stram内容
    parser = PDFParser(pdf_stream)
    doc = PDFDocument(parser, password=password, caching=True)

    # 获取info # 获取metadata（如果有）
    info, metadata = process_doc(doc)

    # 获取pdf text信息和annots列表
    text, annots_list, maxpage = process_pages(doc)

    links, refs = [], []

    # 处理annots，查找link
    for annots in annots_list:
        annots_links = process_annots(annots)
        if annots_links:
            links.extend(annots_links)

    # 处理text，查找link和ref
    text_links, text_refs = process_text(text)

    links.extend(text_links)
    refs.extend(text_refs)

    pdf_dict = {
        'text': text,
        'info': info,
        'metadata': metadata,
        'links': links,
        'refs': refs
    }
    return pdf_dict

