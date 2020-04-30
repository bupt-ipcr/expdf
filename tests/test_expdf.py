#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-30 12:12
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
            'Wireless caching: technical misconceptions and business barriers,',
            'Optimal Cooperative Content Caching and Delivery Policy for Heterogeneous Cellular Networks,', 
            'Joint Caching, Routing, and Channel Assignment for Collaborative Small-Cell Cellular Net-works,',
            'On the Complexity of Optimal Content Placement in Hierarchical Caching Networks,',
            'L. Lei, D. Yuan, C. K. Ho, and S. Sun, “A uniﬁed graph labeling algorithm for consecutive-block channel allocation in SC-FDMA, IEEE Trans. Wireless Commun., vol. 12, no. 11, pp. 5767-5779, Nov. 2013',
            'Efﬁcient processing of deep neural networks: A tutorial and survey',
            'Resource Man-agement with Deep Reinforcement Learning',
            'Edge Caching at Base Stations with Device-to-Device Ofﬂoading',
            'Optimal cell clustering and activation for energy saving in load-coupled wireless networks,',
            'K. Murty, Linear programming, Wiley, 1983.',
            'Minimum-Time Link Scheduling for Emptying Wireless Systems: Solution Characterization and Algorithmic Framework,'
        ]
        
        assert self.expdf_parser.refs == aims


TestExPDF.setup_class()