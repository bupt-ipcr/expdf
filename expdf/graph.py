#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-17 10:56
@FilePath: /expdf/graph.py
@desc: 制作PDF图结构
"""
from collections import namedtuple
from .parser import ExPDFParser
import logging

class PDFNode:
    instances = {}

    def __new__(cls, title, refs=None):
        """保证每个title对应一个PDFNode对象
        创建对象的时候如果title已经有对应对象，就返回该对象
        若没有，则新建对象
        
        对于有对应对象的情况，还要检查refs是否相等。因为这相当于一次
        get，不能改变属性
        """
        if title in cls.instances:
            obj = cls.instances[title]
            logging.info({actient.title for actient in obj.actients}, set(refs))
            if {actient.title for actient in obj.actients} == set(refs) or refs is None:
                return obj
            else:
                raise TypeError("Can't instantiate PDFNode with same title but different refs")
        else:
            obj = object.__new__(cls)
            cls.instances[title] = obj
            return obj

    def __init__(self, title, refs=[]):
        logging.info(f'init node with title {title}, instance_flag is {title in self.instances}')
        self.title = title
        self.parents = []
        if not hasattr(self, 'actients'):
            self.actients = [PDFNode(ref) for ref in refs]
