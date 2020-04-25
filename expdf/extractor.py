#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-25 17:58
@FilePath: /expdf/extractor.py
@desc: 
"""
import re


def get_ref_title(ref_text):
    """从引用文本中匹配引用文章标题

    使用不同的标准格式匹配title，匹配失败的使用文本作为title返回
    考虑到分割获取ref_text的文本会有污染，使用re.search查找
    
    @param: ref_text: 引用原文
    @return: ref title 引用文章的标题
    """
    ref_title = ref_text
    
    # e.g. `W. Jiang, G. Feng and S. Qin, “Optimal Cooperative Content Cachingand Delivery Policy for Heterogeneous Cellular Networks,” in IEEETransactions on Mobile Computing, vol. 16, no. 5, pp. 1382-1393, May2017.`
    if re.search(r'''([^“]+),\s*“(.+)”.*(in|In|IN).''', ref_text):
        ref_title = re.search(r'''([^“]+),\s*“(.+)”.*(in|In|IN).''', ref_text).groups()[1]
    return ref_title
