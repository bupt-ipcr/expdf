#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-17 21:27
@FilePath: /expdf/graph.py
@desc: 制作PDF图结构
"""
from collections import deque, defaultdict
from functools import reduce
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
                group 设置为 cur_group
            2. 遍历cur_node.actients
                - 将actient_node.level 的下限设置为cur_node.level + 1
                即：max(actient_node.level, cur_node.level+1)
                - 如果actient_node未被探索过，则添加到calc_queue中
            3. 遍历cur_node.posterities
                - 将 posterity_node.level 的上限设置为cur_node.level - 1
                即：min(posterity_node.level, cur_node.level-1)
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

    def calculate(self):
        """计算图关系"""
        self.initialize()
        self.explore()
        self.reorganize()

    def initialize(self):
        """初始化信息"""
        for node in self.nodes:
            node.level = 0
            node.status = 'unexplored'
        self.calc_queue = deque()
        self.cur_group = 0

    def explore(self):
        """探索所有节点，设置信息"""
        nodes, calc_queue, cur_group = self.nodes, self.calc_queue, self.cur_group
        # 准备记录group信息
        groups = {}
        # 外层循环，遍历nodes
        for node in nodes:
            # 探索过的节点直接略过
            if node.status == 'explored':
                continue

            # 未探索过的节点压入计算队列
            cur_group += 1
            group_nodes = []  # 重置节点列表
            calc_queue.append(node)

            # 依次弹出node直到没有为止
            while len(calc_queue):
                cur_node = calc_queue.popleft()
                # 设置信息
                cur_node.group = cur_group
                cur_node.status = 'explored'
                # 处理 actients
                for actient in cur_node.actients:
                    actient.level = max(actient.level, cur_node.level + 1)
                    if actient.status == 'unexplored':
                        calc_queue.append(actient)
                # 处理 posterities
                for posterity in cur_node.posterities:
                    posterity.level = min(posterity.level, cur_node.level - 1)
                    if posterity.status == 'unexplored':
                        calc_queue.append(posterity)
                # 节点添加到group列表中
                group_nodes.append(node)

            # 记录节点列表
            groups[cur_group] = group_nodes

        # 记录信息
        self.nodes, self.calc_queue, self.cur_group = nodes, calc_queue, cur_group
        self.groups = groups

        def reorganize(self):
            """重整节点"""
            groups = self.groups
            records = {}
            for gid, nodes in groups.items():
                # 获得最大的level
                max_level = reduce(max, (node.level for node in nodes))
                # 以max_level 为基准重设 level，并记录
                levels = defaultdict(list)
                for node in nodes:
                    node.level = node.level - max_level
                    levels[node.level].append(node)
                # 获取重整后的最小level
                min_level = reduce(min, (node.level for node in nodes))

                # 从0开始向下遍历level，获取当前层的level
                level = 0
                while True:
                    cur_nodes, next_nodes = levels[level], levels[level - 1]

                    # 如果没有下一层的节点，则应该结束
                    if not next_nodes:
                        break

                    # 尝试建立父子关系
                    for cur_node in cur_nodes:
                        for next_node in next_nodes:
                            if next_node in cur_node.posterities:
                                cur_node.children.add(next_node)
                                next_node.parents.add(cur_node)

                    # 每次遍历结束的时候降低一层level
                    level -= 1

                # 保存levels
                records[gid] = levels

            # 确保信息被保存
            self.groups, self.records = groups, records
