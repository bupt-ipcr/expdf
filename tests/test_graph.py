#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-16 22:46
@FilePath: /tests/test_graph.py
@desc: 
"""

from expdf.graph import PDFNode

def test_newnode():
    """测试node的new方法"""
    n0 = PDFNode('title0')
    n0copy = PDFNode('title0')
    n1 = PDFNode('title1')
    
    # n0 和 n0copy 应该是一个对象
    assert n0 is n0copy
    assert n0 is not n1