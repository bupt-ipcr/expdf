#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-29 19:58
@FilePath: /tests/test_extractor.py
@desc: 测试extractor中匹配效果
"""
from expdf.extractor import (
    Link,
    get_ref_title,
    get_urls,
    get_arxivs,
    get_dois,
    get_links
)


def test_get_ref_title():
    # 引号引用类型
    ref_1 = '''W. Jiang, G. Feng and S. Qin, “Optimal Cooperative Content Cachingand Delivery Policy for Heterogeneous Cellular Networks,” in IEEETransactions on Mobile Computing, vol. 16, no. 5, pp. 1382-1393, May2017.'''
    assert get_ref_title(ref_1) == 'Optimal Cooperative Content Cachingand Delivery Policy for Heterogeneous Cellular Networks,'
    # 分句引用类型
    ref_2 = '''L. Breslau, Pei Cao, Li Fan, G. Phillips, and S. Shenker. Web caching and zipf-like distributions: evidence and implications. In INFOCOM ’99. Eighteenth Annual Joint Conference of the IEEE Computer and Communications Societies. Proceedings. IEEE, volume 1, pages 126–134 vol.1, Mar 1999.'''
    assert get_ref_title(ref_2) == 'Web caching and zipf-like distributions: evidence and implications'
    # 暂时无法匹配的类型
    ref_3 = '''My title.: “123”, 1998'''
    assert get_ref_title(ref_3) == 'My title.: “123”, 1998'


def test_get_urls():
    # 匹配所有url
    long_text = '''my first pdf: https://www.demo1.com/h3.pdf
                my second pdf: github.io/mypage/h4.html'''
    urls = get_urls(long_text)
    link1 = Link('pdf', 'https://www.demo1.com/h3.pdf', 'https://www.demo1.com/h3.pdf')
    link2 = Link('url', 'github.io/mypage/h4.html', 'github.io/mypage/h4.html')
        
    assert link1 in urls
    assert link2 in urls

    # 匹配仅有的url
    short_text = ''' bupt.edu.cn/xxx.pdf '''
    s_url = get_urls(short_text)[0]
    assert s_url == Link('pdf', 'bupt.edu.cn/xxx.pdf', 'bupt.edu.cn/xxx.pdf')

    # 如果没有url
    none_text = '''here is my sentence and contains no urls'''
    assert get_urls(none_text) == []


def test_get_arxivs():
    # 匹配描述格式的arxiv
    arxiv_text_1 = '''arXiv preprint arXiv:1312.5602, 2013.'''
    assert get_arxivs(arxiv_text_1) == {'1312.5602'}

    arxiv_text_2 = ''' arXiv.org.1511.0658'''
    assert get_arxivs(arxiv_text_2) == {'1511.0658'}

    arxiv_text_v1 = '''X. Zhang and L. Duan, “Optimal deployment of UAV net- works for delivering emergency wireless coverage,” 2017, arXIV:1710.05616v1.'''
    assert get_arxivs(arxiv_text_v1) == {'1710.05616v1'}

    # 匹配链接格式的arxiv
    arxiv_url = '''.. link is https://arxiv.org/abs/1812.02979 '''
    assert get_arxivs(arxiv_url) == {'1812.02979'}


def test_get_dois():
    # 匹配文本格式的DOI
    doi_text = '''Catalog IDs
    DOI: 10.1109/INFCOMW.2019.8845154
    ISBN: 9781728118789'''
    assert get_dois(doi_text) == {'10.1109/INFCOMW.2019.8845154'}

    # 匹配url格式的DOI
    doi_url = '''Demos·August 2019 · Pages 114-115 · https://doi.org/10.1145/3342280/3342327'''
    assert get_dois(doi_url) == {'10.1145/3342280/3342327'}
