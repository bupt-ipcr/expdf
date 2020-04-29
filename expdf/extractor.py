#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-29 20:33
@FilePath: /expdf/extractor.py
@desc: 匹配
"""
import re


class Link:
    def __init__(self, linktype, uri, link):
        self.linktype, self.uri, self.link = linktype, uri, link

    def __eq__(self, other):
        # 兼容http与https的差异
        return self.link == other.link or self.link.replace('https', 'http') == other.link.replace('https', 'http')

    def equal(self, other):
        """严格定义相等"""
        return self.uri == other.uri and self.linktype == other.linktype and self.link == other.link


def get_ref_title(ref_text):
    """从引用文本中匹配引用文章标题

    使用不同的标准格式匹配title，匹配失败的使用文本作为title返回
    考虑到分割获取ref_text的文本会有污染，使用re.search查找

    @param: ref_text: 引用原文
    @return: ref title 引用文章的标题
    """
    # e.g. W. Jiang, G. Feng and S. Qin, “Optimal Cooperative Content Cachingand Delivery Policy for Heterogeneous Cellular Networks,” in IEEETransactions on Mobile Computing, vol. 16, no. 5, pp. 1382-1393, May2017.
    if re.search(r'''([^“]+),\s*“(.+)”.*(in|In|IN)''', ref_text):
        return re.search(r'''([^“]+),\s*“(.+)”.*(in|In|IN)''', ref_text).groups()[1]
    # e.g. L. Breslau, Pei Cao, Li Fan, G. Phillips, and S. Shenker. Web caching and zipf-like distributions: evidence and implications. In INFOCOM ’99. Eighteenth Annual Joint Conference of the IEEE Computer and Communications Societies. Proceedings. IEEE, volume 1, pages 126–134 vol.1, Mar 1999.
    if re.search(r'''(.+?[^A-Z])\.\s*([^.]+?[^A-Z])\..*(in|In|IN)''', ref_text):
        return re.search(r'''(.+?[^A-Z])\.\s*([^.]+?[^A-Z])\..*(in|In|IN)''', ref_text).groups()[1]

    return ref_text


def get_urls(text):
    """从text中匹配 urls
    @param text: 文本
    @return set, all urls
    """
    # URL
    URL_REGEX = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""

    links = []
    for url in set(re.findall(URL_REGEX, text, re.I)):
        if url.lower().endswith('pdf'):
            links.append(Link('pdf', url, url))
        else:
            links.append(Link('url', url, url))
    return links


def get_arxivs(text):
    """从text中匹配 arxivs
    @param text: 文本
    @return set, all arxivs
    """
    re_texts = [r"""arxiv:\s?([^\s,]+)""", r"""arXiv\.org\.\s?([^\s,]+)"""]
    re_url = r"""arxiv.org/abs/([^\s,]+)"""
    arxivs = []
    for re_text in re_texts:
        arxivs.extend(re.findall(re_text, text, re.I))
    arxivs.extend(re.findall(re_url, text, re.I))

    links = [Link('arxiv', arxiv, f'https://arxiv.org/abs/{arxiv}') for arxiv in set([r.strip(".") for r in arxivs])]
    return links


def get_dois(text):
    """从text中匹配 dois
    @param text: 文本
    @return set, all dois
    """
    re_text = r"""DOI:\s?([^\s,]+)"""
    re_url = r'''https?://doi.org/([^\s,]+)'''

    dois = []
    dois.extend(re.findall(re_text, text, re.I))
    dois.extend(re.findall(re_url, text, re.I))
    links = [Link('doi', doi, f'https://doi.org/{doi}') for doi in set([r.strip(".") for r in dois])]
    return links


def get_links(text):
    """获取uri中包含的所有link
    依次用arxiv, doi, url规则匹配links
    对于url匹配的结果，要查找有没有相等的Link，避免出现重复

    @param text: 需要处理的文本
    @return: list link列表
    """
    links = []
    # 对于arxiv和doi，不考虑重复
    links.extend(get_arxivs(text))
    links.extend(get_dois(text))
    # 对于url要检查重复
    for link in get_urls(text):
        if link not in links:
            links.append(link)

    return links
