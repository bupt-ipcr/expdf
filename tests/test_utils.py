#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-28 12:09
@FilePath: /tests/test_utils.py
@desc: 测试utils
"""

from expdf.utils import Link, flatten


def test_flatten():
    s1 = Link(1, 'a', 1)
    s2 = Link(2, 'a', 2)
    s3 = Link(3, 'a', 3)
    s4 = Link(4, 'a', 4)
    s5 = Link(5, 'a', 5)

    l1 = [s1, [s2, [s3, [s4, None]]]]
    fl1 = flatten(l1)
    assert fl1 == [s1, s2, s3, s4]

    l2 = [s1, [s2, s3, s4], s5]
    fl2 = flatten(l2)
    assert fl2 == [s1, s2, s3, s4, s5]
