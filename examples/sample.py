#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-19 16:56
@FilePath: /text.py
@desc: 
"""
from expdf.graph import PDFNode, LocalPDFNode, Graph
from expdf.visualize import render
from expdf.parser import ExPDFParser
from pprint import pprint

expdf_parser = ExPDFParser("tests/test.pdf")
localPDFNode = LocalPDFNode(expdf_parser.title, expdf_parser.refs)
graph = Graph()
graph.calculate()
render(graph.infos, 'svg.html')

