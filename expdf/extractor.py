#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-25 17:49
@FilePath: /expdf/extractor.py
@desc: 
"""
import re


def get_ref_title(ref_text):
    """从引用文本中匹配引用文章标题

    使用不同的标准格式匹配title，匹配失败的使用文本作为title返回
    @param: ref_text: 引用原文
    @return: ref title 引用文章的标题
    """
    ref_title = ref_text
    return ref_title
