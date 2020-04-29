#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-29 20:54
@FilePath: /tests/test_visualize.py
@desc: visualize的测试
"""
from expdf.graph import LocalPDFNode, Graph
from expdf.visualize import render
from expdf.parser import ExPDFParser
from pathlib import Path

# ! 在Windows上的表现未知！
tmp = Path('/tmp').resolve()
svg = tmp / 'svg.html'

def test_visualize():
    expdf_parser = ExPDFParser("tests/test.pdf")
    LocalPDFNode(expdf_parser.title, expdf_parser.refs)
    graph = Graph()
    graph.calculate()
    render(graph.infos, svg.resolve())
    

    # 验证是否render
    assert svg.exists()
    # 验证行数为172
    with svg.open('r') as f:
        assert len(f.readlines()) == 172


