#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-28 12:12
@FilePath: /tests/test_graph.py
@desc: 测试Graph模块是否正常工作
"""

from expdf.graph import PDFNode, LocalPDFNode, Graph


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
        except Exception:
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
        except Exception:
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
        assert na.posterities == {n0}


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
            LocalPDFNode('title0', refs=['ta', 'tc'])
        except Exception:
            has_except = True

        assert has_except == False, "Unexpected error in override LocalPDFNode instance"

        assert n0.actients == {PDFNode('ta'), PDFNode('tc')}
        assert PDFNode.get_nodes() == [PDFNode('title0'), PDFNode('ta'), PDFNode('tb'), PDFNode('tc')]


class TestGraph:
    """测试graph计算"""
    @classmethod
    def setup_class(cls):
        PDFNode.clear_nodes()

    @classmethod
    def teardown_class(cls):
        PDFNode.clear_nodes()

    def test_graph_calc(self):
        LocalPDFNode('title0', refs=['title1', 'title2'])
        LocalPDFNode('title1', refs=['title3'])
        LocalPDFNode('title2', refs=['title3'])
        graph = Graph()
        graph.calculate()

        infos = graph.infos

        assert infos[0]['levels'][0] == [{'children_titles': {'title2', 'title1'},
                                          'local_file': False,
                                          'parents_titles': set(),
                                          'title': 'title3'}]
        assert any((
            infos[0]['levels'][-1] == [{'children_titles': {'title0'},
                                        'local_file': True,
                                        'parents_titles': {'title3'},
                                        'title': 'title2'},
                                       {'children_titles': {'title0'},
                                        'local_file': True,
                                        'parents_titles': {'title3'},
                                        'title': 'title1'}],
            infos[0]['levels'][-1] == [{'children_titles': {'title0'},
                                        'local_file': True,
                                        'parents_titles': {'title3'},
                                        'title': 'title1'},
                                       {'children_titles': {'title0'},
                                        'local_file': True,
                                        'parents_titles': {'title3'},
                                        'title': 'title2'}]
        ))
        assert infos[0]['levels'][-2] == [{'children_titles': set(),
                                           'local_file': True,
                                           'parents_titles': {'title2', 'title1'},
                                           'title': 'title0'}]
        assert infos[0]['min_level'] == -2
