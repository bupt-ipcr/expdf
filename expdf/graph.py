#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-17 11:33
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
            
            logging.info('get', title, obj.actients)
            logging.info({actient.title for actient in obj.actients}, set(refs) if refs is not None else set())
            
            if refs is None or {actient.title for actient in obj.actients} == set(refs):
                return obj
            else:
                raise TypeError("Can't instantiate PDFNode with same title but different refs")
        else:
            obj = object.__new__(cls)
            cls.instances[title] = obj
            
            # 对于新建对象，需要进行赋值处理
            obj.title = title
            obj.parents, obj.children = set(), set()
            obj.posterity = set()
            obj.actients = {PDFNode(ref) for ref in refs} if refs is not None else set()
            for node in obj.actients:
                node.posterity.add(obj)
            
            logging.info('create', title, obj.actients)
            
            return obj

    @classmethod
    def get_nodes(cls):
        return list(cls.instances.values())
    
    @classmethod
    def clear_nodes(cls):
        cls.instances.clear()