#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-19 16:20
@FilePath: /caoxiaojing/expdf/expdf/templates.py
@desc: templates
"""
svg_template = '''
<html>
  <head>   
    <style type="text/css">
    circle{
      fill: white;
      stroke: black;
      stroke-width: 1;
    }
    line{
      stroke: black;
      stroke-width: 1px;
    }
    text{
      display: none;
    }
    .node:hover circle{
      fill: white;
      stroke-width: 2px;
    }
    .node:hover line{
      stroke: black;
      stroke-width: 2px;
    }
    .node:hover text{
      fill: black;
      color: black;
      display: block;
    }
    .local{
      stroke: orange;
    }
    .nonlocal{
      stroke: black;
    }
    </style>
  </head>
  <body>
    <div style="margin:100px">
    SVG_CONTENT
    </div>
  </body>
</html>
'''


