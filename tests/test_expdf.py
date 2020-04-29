#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-29 20:45
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
            'V. Sze, Y. Chen, T. Yang, and J. Emer, “Efﬁcient processing of deepneural networks: A tutorial and survey”, http://arxiv.org/abs/1703.09039,Mar. 2017.',
            'H. Mao, M. Alizadeh, I. Menache, and S. Kandula. “Resource Man-agement with Deep Reinforcement Learning”, In Proceedings of the 15thACM Workshop on Hot Topics in Networks (HotNets). ACM, New York,USA, 50-56, 2016.',
            'Edge Caching atBase Stations with Device-to-Device Ofﬂoading',
            'Optimal cell clustering andactivation for energy saving in load-coupled wireless networks,',
            'K. Murty, Linear programming, Wiley, 1983.',
            'Minimum-Time LinkScheduling for Emptying Wireless Systems: Solution Characterizationand Algorithmic Framework,'
        ]
        
        assert self.expdf_parser.refs == aims

