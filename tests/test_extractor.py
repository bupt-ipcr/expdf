#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-28 18:09
@FilePath: /tests/test_extractor.py
@desc: 测试extractor中匹配效果
"""
from expdf.extractor import get_ref_title, get_urls


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
                my second pdf: github.io/mypage/h4.pdf'''
    assert get_urls(long_text) == {'https://www.demo1.com/h3.pdf', 'github.io/mypage/h4.pdf'}

    # 匹配仅有的url
    short_text = ''' bupt.edu.cn/xxx.pdf '''
    assert get_urls(short_text) == {'bupt.edu.cn/xxx.pdf'}

    # 如果没有url
    none_text = '''here is my sentence and contains no urls'''
    assert get_urls(none_text) == set()
