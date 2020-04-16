#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-16 22:43
@FilePath: /expdf/graph.py
@desc: 制作PDF图结构
"""
from collections import namedtuple
from .parser import ExPDFParser

class PDFNode:
    def __init__(self, title, refs=[]):
        self.title = title
        self.parents = []
        self.actients = [PDFNode(ref) for ref in refs]

