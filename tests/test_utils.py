#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-16 22:35
@FilePath: /tests/test_utils.py
@desc: 测试utils
"""

from expdf.utils import Reference, flatten

def test_flatten():
    s1 = Reference(1, 'a')
    s2 = Reference(2, 'a')
    s3 = Reference(3, 'a')
    s4 = Reference(4, 'a')
    s5 = Reference(5, 'a')
    
    l = [s1, [s2, [s3, [s4, None]]]]
    fl = flatten(l)
    assert fl == [s1, s2, s3, s4]
    
    l = [s2, [s2, s3, s4], s5]
    fl = flatten(l)
    assert fl == [s1, s2, s3, s4, s5]