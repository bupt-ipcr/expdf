#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-17 21:07
@FilePath: /tests/test_graph.py
@desc: 
"""

from expdf.graph import PDFNode, LocalPDFNode


class TestPDFNode:
    @classmethod
    def setup_class(cls):
        PDFNode.clear_nodes()
        
    @classmethod
    def teardown_class(cls):
        PDFNode.clear_nodes()

    def test_new(self):
        """测试新建node是否表现正常"""
        n0 = PDFNode('title0', refs=['ta', 'tb'])
        
        # 创建和n0同名对象时，使用相同ref应该不报错
        has_except = False
        try:
            n0 = PDFNode('title0', refs=['ta', 'tb'])
        except Exception as e:
            has_except = True
        assert has_except == False, "Unexpected error in creating PDFNode instance"
        
        # 使用不同ref应该会报错
        has_except = False
        try:
            n0copy = PDFNode('title0', [])
        except Exception as e:
            assert str(e) == "Can't instantiate PDFNode with same title but different refs"
            has_except = True
        assert has_except == True, "Create two instance of PDFNode with different refs has no error"
        
        # 不指明refs则不会报错
        has_except = False
        try:
            n0copy = PDFNode('title0')
        except Exception as e:
            has_except = True
        assert has_except == False, "Unexpected error in creating PDFNode instance"
        
        # n0 和 n0copy 应该是一个对象
        assert n0 is n0copy
        
        # 所有用到的node都应该被创建
        nodes = PDFNode.get_nodes() 
        assert nodes == [n0, PDFNode('ta'), PDFNode('tb')]


    def test_relations(self):
        """测试节点之间祖先/子孙关系是否正常"""
        n0 = PDFNode('title0', refs=['ta', 'tb'])
        na, nb = PDFNode('ta'), PDFNode('tb')
        
        # n0 祖先应该是ta, tb
        assert n0.actients == {na, nb}
        
        # ta对象应该有posterity，但是没有children
        assert na.children == set()
        assert na.posterity == {n0}

class TestLocalPDFNode:
    @classmethod
    def setup_class(cls):
        PDFNode.clear_nodes()
        
    @classmethod
    def teardown_class(cls):
        PDFNode.clear_nodes()

    def test_override(self):
        """测试新建node是否表现正常"""
        n0 = LocalPDFNode('title0', refs=['ta', 'tb'])
        
        has_except = False
        try:
            n0 = LocalPDFNode('title0', refs=['ta', 'tc'])
        except Exception as e:
            has_except = True
            
        assert has_except == False, "Unexpected error in override LocalPDFNode instance"
        
        assert n0.actients == {PDFNode('ta'), PDFNode('tb')}
        assert PDFNode.get_nodes == {PDFNode('n0'), PDFNode('ta'), PDFNode('tb'), PDFNode('tc')}
        
        