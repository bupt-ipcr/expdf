#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-30 11:17
@FilePath: /tests/test_expdf.py
@desc: 测试expdf
"""


from expdf.graph import PDFNode, LocalPDFNode, Graph
from expdf.visualize import render
from expdf.parser import ExPDFParser


class TestExPDF:
    @classmethod
    def setup_class(cls):
        cls.expdf_parser = ExPDFParser("tests/test.pdf")

    def test_links(self):
        aims = {
            ('arxiv', '1703.09039'),
            ('url', 'thang.vu'),
            ('url', 'uu.se')
        }
        
        links = {(link.linktype, link.uri) for link in self.expdf_parser.links}
        
        assert links == aims

    def test_refs(self):
        aims = [
            'Wirelesscaching: technical misconceptions and business barriers,',
            'Optimal Cooperative Content Cachingand Delivery Policy for Heterogeneous Cellular Networks,', 
            'Joint Caching, Routing,and Channel Assignment for Collaborative Small-Cell Cellular Net-works,',
            'On the Complexity of Optimal ContentPlacement in Hierarchical Caching Networks,',
            'L. Lei, D. Yuan, C. K. Ho, and S. Sun, “A uniﬁed graph labelingalgorithm for consecutive-block channel allocation in SC-FDMA, IEEETrans. Wireless Commun., vol. 12, no. 11, pp. 5767-5779, Nov. 2013',
            'Efﬁcient processing of deepneural networks: A tutorial and survey',
            'Resource Man-agement with Deep Reinforcement Learning',
            'Edge Caching atBase Stations with Device-to-Device Ofﬂoading',
            'Optimal cell clustering andactivation for energy saving in load-coupled wireless networks,',
            'K. Murty, Linear programming, Wiley, 1983.',
            'Minimum-Time LinkScheduling for Emptying Wireless Systems: Solution Characterizationand Algorithmic Framework,'
        ]
        
        assert self.expdf_parser.refs == aims


TestExPDF.setup_class()