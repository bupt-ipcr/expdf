#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-15 11:48
@FilePath: /xxpdf.py
@desc: 
"""
from ref_resolve import resolve_PDFObjRef
import re
from xmp import xmp_to_dict
from io import BytesIO
from pdfminer.layout import LAParams
from pdfminer.converter import TextConverter
from pdfminer.pdftypes import resolve1, PDFObjRef
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer import psparser
from pprint import pprint
import json
from pdfminer import settings as pdfminer_settings
pdfminer_settings.STRICT = False


def extract_urls(text):
    # URL
    URL_REGEX = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""
    return set(re.findall(URL_REGEX, text, re.IGNORECASE))


def extract_arxiv(text):
    # arXiv.org
    ARXIV_REGEX = r"""arxiv:\s?([^\s,]+)"""
    ARXIV_REGEX2 = r"""arxiv.org/abs/([^\s,]+)"""
    res = re.findall(ARXIV_REGEX, text, re.IGNORECASE) + re.findall(ARXIV_REGEX2, text, re.IGNORECASE)
    return set([r.strip(".") for r in res])


def extract_doi(text):
    # DOI
    DOI_REGEX = r"""DOI:\s?([^\s,]+)"""
    res = set(re.findall(DOI_REGEX, text, re.IGNORECASE))
    return set([r.strip(".") for r in res])


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


def process_text(doc: PDFDocument):
    """处理doc文档中的text信息
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
            annots_list.append((page.annots, curpage))

    # Get text from stream
    text = text_io.getvalue().decode("utf-8")
    text_io.close()
    converter.close()
    maxpage = curpage
    return text, annots_list, maxpage


def resolve_pdf(uri='test.pdf', password='', pagenos=[], maxpages=0):
    # 将PDF文件打开为stream
    pdf_stream = open(uri, "rb")

    # 使用PDFMiner解析stram内容
    parser = PDFParser(pdf_stream)
    doc = PDFDocument(parser, password=password, caching=True)

    # 获取metadata（如果有）
    metadata = get_metadata(doc)
    text, annots_list, maxpage = process_text(doc)
    
    references = []
    for annots_item in annots_list:
        refs = resolve_PDFObjRef(*annots_list)
        if refs:
            if isinstance(refs, list):
                for ref in refs:
                    if ref:
                        references.append(ref)
            references.append(refs)


    # Extract URL references from text
    for url in extract_urls(text):
        references.append((url, maxpage))

    for ref in extract_arxiv(text):
        references.append((ref, maxpage))

    for ref in extract_doi(text):
        references.append((ref, maxpage))

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
