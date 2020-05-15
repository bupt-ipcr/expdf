#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-05-15 11:48
@FilePath: /expdf/expdf/parser.py
@desc: parser of expand PDF
"""
from io import BytesIO
from pathlib import Path
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
import requests
from .extractor import get_urls
from .processors import process_doc, process_pages, process_annots, process_text


class ExPDFParser:
    """ExPDFParser(uri="", local=False, strict=False)

    Enhanced infomations of a PDF object, includes title of the PDF,
    all kinds of links inside PDF content, citations listed in 
    `References`, info and metadate attribute of the PDF object.

    The parser is built on pdfminer to resolve PDF object, mainly
    use regex to extract links and citations from content of PDF.

    Parameters
    ----------
    uri : str, resource uri, local file location or a url.

    local : bool, default False, set to True to force use local file.

    strict : bool, default False, set to True to enable strict mode.
        In strict mode, if title cannot be found in a citation
        record, it will be ignored. If not in strict mode, complete
        citation will be returned as the title.

    Attributes
    ----------
    title : str, title of PDF.
        Title will be searched in info and metadate attribute of the
        PDF object, and if not found, it returns filename of uri.

    links : list of inks in content of PDF.
        The parser use regex to extract links, and return it as a simple
        class `Link` with its type, uniform resource identifier and link.

    refs : list of citation titles list in `References` part of the PDF.
        The parser try to find out `References` part, seperate for each
        line, then use regex to extract paper title in the citation line.
    
    info : dict for attribute info of the PDF object.

    metadata : dict for attribute metadata of the PDF object.

    Examples
    --------
    Use ExPDFParser to resolve PDF.
    >>> from expdf import ExPDFParser
    >>> pdf = ExPDFParser("pdfs/test.pdf")
    >>> pdf.title
    'A Deep Learning Approach for Optimizing Content Delivering in Cache-Enabled HetNet'
    >>> for ref in pdf.refs:
    ...     print(f'- {ref}')
    ... 
    - Wireless caching: technical misconceptions and business barriers,
    - Optimal Cooperative Content Caching and Delivery Policy for Heterogeneous Cellular Networks,
    - Joint Caching, Routing, and Channel Assignment for Collaborative Small-Cell Cellular Net-works,
    - On the Complexity of Optimal Content Placement in Hierarchical Caching Networks,
    - Wireless Commun
    - Efﬁcient processing of deep neural networks: A tutorial and survey
    - Resource Man-agement with Deep Reinforcement Learning
    - Edge Caching at Base Stations with Device-to-Device Ofﬂoading
    - Optimal cell clustering and activation for energy saving in load-coupled wireless networks,
    - K. Murty, Linear programming, Wiley, 1983.
    - Minimum-Time Link Scheduling for Emptying Wireless Systems: Solution Characterization and Algorithmic Framework,

    """

    def __init__(self, uri, local=False):
        filename, stream = get_stream(uri)
        expdf = ex_parser(stream)
        expdf.update({
            'filename': filename
        })
        self._data = expdf

    @property
    def title(self):
        info, metadata = self._data['info'], self._data['metadata']
        # 尝试从info中恢复title
        if 'Title' in info:
            title = info['Title']
            if isinstance(title, bytes):
                if title.decode('utf-8').strip():
                    return title.decode('utf-8').strip()
            else:
                if title.strip():
                    return title.strip()
        # 如果失败，尝试从metadata获取
        if 'dc' in metadata:
            if 'title' in metadata['dc'] and metadata['dc']['title']['x-default'].strip():
                return metadata['dc']['title']['x-default']
            
        # 如果找不到则用filename代替
        return self._data['filename']

    @property
    def links(self):
        return self._data['links']

    @property
    def refs(self):
        return self._data['refs']

    @property
    def info(self):
        return self._data['info']

    @property
    def metadata(self):
        return self._data['metadata']


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
            filename, stream = path.with_suffix('').name, path.open("rb")
    else:
        content = requests.get(uri).content
        filename, stream = uri.split("/")[-1], BytesIO(content)

    return filename, stream


def ex_parser(pdf_stream, password='', pagenos=[], maxpages=0):
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
