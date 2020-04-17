#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-17 10:59
@FilePath: /tests/test_graph.py
@desc: 
"""

from expdf.graph import PDFNode

def test_newnode():
    """测试node的new方法"""
    n0 = PDFNode('title0', refs=['ta', 'tb'])
    
    
    # 创建和n0同名对象时，使用相同ref应该不报错
    has_except = False
    try:
        n0 = PDFNode('title0', refs=['ta', 'tb'])
    except Exception as e:
        has_except = True
    assert has_except == False, "Unexpected error in creating PDFNode instance"
    
    has_except = False
    try:
        n0copy = PDFNode('title0', [])
    except Exception as e:
        assert str(e) == "Can't instantiate PDFNode with same title but different refs"
        has_except = True
    assert has_except == True, "Create two instance of PDFNode with different refs has no error"
    
    # 不指明refs则不会报错
    n0copy = PDFNode('title0')
    
    # n0 和 n0copy 应该是一个对象
    assert n0 is n0copy
    # n0的属性应该正确
    assert n0.title == 'title0'
    # n0的refs不应该被覆盖
    assert n0.actients == [PDFNode('ta'), PDFNode('tb')]