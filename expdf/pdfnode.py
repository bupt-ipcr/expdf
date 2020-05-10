#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-05-10 10:08
@FilePath: /expdf/expdf/graph.py
@desc: 制作PDF图结构
"""
from collections import deque, defaultdict
from functools import reduce
import logging
import re


class PDFNode:
    instances = {}

    def __new__(cls, title, refs=None):
        """保证每个title对应一个PDFNode对象
        创建对象的时候如果title已经有对应对象，就返回该对象
        若没有，则新建对象

        对于有对应对象的情况，还要检查refs是否相等。因为这相当于一次
        get，不能改变属性
        """
        node_key = re.sub(r'\W', '', title.lower())
        if node_key in cls.instances:
            obj = cls.instances[node_key]

            logging.info('get', title, obj.actients)

            if refs is None or {actient.title for actient in obj.actients} == set(refs):
                return obj
            else:
                raise TypeError("Can't instantiate PDFNode with same title but different refs")
        else:
            obj = object.__new__(cls)
            cls.instances[node_key] = obj

            # 对于新建对象，需要进行赋值处理
            obj.node_key = node_key
            obj.title, obj.local_file = title, False
            obj.parents, obj.children = set(), set()
            obj.posterities = set()
            obj.actients = {PDFNode(ref) for ref in refs} if refs is not None else set()
            for node in obj.actients:
                node.posterities.add(obj)

            logging.info('create', title, obj.actients)

            return obj

    @classmethod
    def get_nodes(cls):
        return list(cls.instances.values())

    @classmethod
    def clear_nodes(cls):
        cls.instances.clear()

    def set_refs(self, refs):
        """提供set refs的方法"""
        self.actients = {PDFNode(ref) for ref in refs} if refs is not None else set()
        for node in self.actients:
            node.posterities.add(self)


class LocalPDFNode(PDFNode):
    """如果是本地文件，允许创建时覆盖ref"""
    def __new__(cls, title, refs=None):
        """获取实例的时候略过refs，在init的时候设置"""
        obj = PDFNode(title)
        obj.local_file = True
        if refs is not None:
            obj.set_refs(refs)
        return obj
