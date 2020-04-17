#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-17 20:08
@FilePath: /expdf/graph.py
@desc: 制作PDF图结构
"""
from collections import deque
import logging
from .parser import ExPDFParser

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
        
        
class Graph:
    """计算所有PDFNode之间的图关系
    
    nodes是所有PDFNode实例的集合
    判断层级关系
    - 初始化
        为所有node初始化级别 level=0
        为所有node设置状态 status='unexplored'
        初始化队列 calc_queue=deque()
        初始化组别 cur_group=0
        获取所有节点 nodes
        
    - 遍历nodes
        从nodes中pop一个 status=='unexplored' 的节点。若节点 status!='unexplored'，
        略过这个节点，pop下一个节点，直到：
        a. 找到一个满足要求的节点
            cur_group += 1， 将这个node推入calc_queue
            开始遍历calc_queue，依次弹出cur_node
            
            1. 将 status 设置为 'explored'
            2. 遍历cur_node.actients
                - 将actient_node.level 的下限设置为cur_node.level + 1
                即：max(actient_node.level, cur_node.level+1)
                - 将 actient_node.group 设置为 cur_group (cur_group 应当和 cur_node.group 一致)
                - 如果actient_node未被探索过，则添加到calc_queue中
            3. 遍历cur_node.posterities
                - 将 posterity_node.level 的上限设置为cur_node.level - 1
                即：min(posterity_node.level, cur_node.level-1)
                - 将 posterity_node.group 设置为 cur_group (cur_group 应当和 cur_node.group 一致)
                - 如果 posterity_node 未被探索过，则添加到calc_queue中
            当calc_queue为空的时候，重复a，直到b
            
        b. 已经结束对nodes的遍历
        
    - 重整nodes
        按照group聚合nodes
        对于每个group：
        1. 查找group中最大的level，设为基准
            以基准为0重整group_nodes中所有node的level
        2. 按照level遍历节点
            设当前level的节点为 cur_level_nodes，下一level的节点为 next_level_nodes
            a. 若 next_level_nodes 存在
                对于每个 cur_level_node， 检查所有 next_level_node，
                若某个下一级的 node 恰好在 posterities 中，则为他们建立父子关系
                即：若 next_level_node in cur_level_node.posterities
                    cur_level_node.children.add(next_level_node)
                    next_level_node.parents.add(cur_level_node)
            b. 若next_level_nodes 不存在，则结束遍历（此时level应该是min_level）
            
    - 返回结果
        遍历所有group，得到如下格式：
        返回结构如下：
            [{group1}, {group2}, ..., {groupn}]
        对于每个group，都是json对象，结构如下：
            {"level0": [{n0i}, .. ], "level1": [{n1i}, .. ], ... "levelm": [{nmi}, ..]}
            即每个level作为key，对应一个list形式的node
        每个node都是一个json对象，包括如下内容：
            {"title": xx, "children_title": [xx, xx, ... xx], "parents_title": [xx, xx, ... xx], "local_file": true}
                
    """
    
    def __init__(self):
        self.nodes = PDFNode.get_nodes()
        
    def initialize(self):
        """初始化信息"""
        for node in self.nodes:
            node.level = 0
            node.status = 'unexplored'
        self.calc_queue = deque()
        self.cur_group = 0
            