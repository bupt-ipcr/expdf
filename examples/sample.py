#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-28 12:08
@FilePath: /examples/sample.py
@desc: 演示使用单个PDF文档产生引用关系图
"""
from expdf.graph import LocalPDFNode, Graph
from expdf.visualize import render
from expdf.parser import ExPDFParser

expdf_parser = ExPDFParser("tests/test.pdf")
localPDFNode = LocalPDFNode(expdf_parser.title, expdf_parser.refs)
graph = Graph()
graph.calculate()
render(graph.infos, 'svg.html')
