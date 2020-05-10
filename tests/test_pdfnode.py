#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-05-10 10:29
@FilePath: /expdf/tests/test_pdfnode.py
@desc: 测试Graph模块是否正常工作
"""

from expdf.pdfnode import PDFNode, LocalPDFNode
import json


class TestPDFNode:
    def setup(self):
        PDFNode.clear_nodes()

    def teardown(self):
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
        assert not has_except, "Unexpected error in creating PDFNode instance"

        # 使用不同ref应该会报错
        has_except = False
        try:
            n0copy = PDFNode('title0', [])
        except Exception as e:
            assert str(e) == "Can't instantiate PDFNode with same title but different refs"
            has_except = True
        assert has_except, "Create two instance of PDFNode with different refs has no error"

        # 不指明refs则不会报错
        has_except = False
        try:
            n0copy = PDFNode('title0')
        except Exception:
            has_except = True
        assert not has_except, "Unexpected error in creating PDFNode instance"

        # n0 和 n0copy 应该是一个对象
        assert n0 is n0copy

        # 所有用到的node都应该被创建
        nodes = PDFNode.nodes()
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

    def test_instances(self):
        """测试记录所有实例的instances是否正常工作
        instances的key应该是小写并去除 非字母数字下划线 字符后的结果
        """
        n0 = PDFNode('A collaborative distributed strategy for multi-agent reinforcement learning through consensus + innovations.')
        # 验证记录的key是否小写且去除特殊符号
        assert list(PDFNode.instances.keys()) == [
            'acollaborativedistributedstrategyformultiagentreinforcementlearningthroughconsensusinnovations']
        # 验证本身的title没变化
        assert n0.title == 'A collaborative distributed strategy for multi-agent reinforcement learning through consensus + innovations.'

        # 验证仅符号不同的Node不会被新建
        n0new = PDFNode(
            '?A collaborative distributed strategy for multi-agent reinforcement learning through consensus + innovations')
        assert n0new == n0

        # 验证字母或数字不同的Node会被新建
        n1 = PDFNode(
            'A new collaborative distributed strategy for multi-agent reinforcement learning through consensus + innovations')
        assert n0 != n1

    def test_get_json(self):
        """test method get_json"""
        PDFNode('title0', ['title2'])
        PDFNode('title1', ['title2'])
        PDFNode('title3', ['title0'])
        pdf_info = json.loads(PDFNode.get_json())
        
        # posterities is a set and convert to list may have different order
        assert pdf_info == [
            {'node_key': 'title0', 'title': 'title0', 'local': False, 'actients': [
                {'node_key': 'title2', 'title': 'title2'}], 'posterities': [{'node_key': 'title3', 'title': 'title3'}]},
            {'node_key': 'title2', 'title': 'title2', 'local': False, 'actients': [], 'posterities': [
                {'node_key': 'title0', 'title': 'title0'}, {'node_key': 'title1', 'title': 'title1'}]},
            {'node_key': 'title1', 'title': 'title1', 'local': False, 'actients': [
                {'node_key': 'title2', 'title': 'title2'}], 'posterities': []},
            {'node_key': 'title3', 'title': 'title3', 'local': False, 'actients': [
                {'node_key': 'title0', 'title': 'title0'}], 'posterities': []}
        ] or pdf_info == [
            {'node_key': 'title0', 'title': 'title0', 'local': False, 'actients': [
                {'node_key': 'title2', 'title': 'title2'}], 'posterities': [{'node_key': 'title3', 'title': 'title3'}]},
            {'node_key': 'title2', 'title': 'title2', 'local': False, 'actients': [], 'posterities': [
                {'node_key': 'title1', 'title': 'title1'}, {'node_key': 'title0', 'title': 'title0'}]},
            {'node_key': 'title1', 'title': 'title1', 'local': False, 'actients': [
                {'node_key': 'title2', 'title': 'title2'}], 'posterities': []},
            {'node_key': 'title3', 'title': 'title3', 'local': False, 'actients': [
                {'node_key': 'title0', 'title': 'title0'}], 'posterities': []}
        ]


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

        assert not has_except, "Unexpected error in override LocalPDFNode instance"

        assert n0.actients == {PDFNode('ta'), PDFNode('tc')}
        assert PDFNode.nodes() == [PDFNode('title0'), PDFNode('ta'), PDFNode('tb'), PDFNode('tc')]
