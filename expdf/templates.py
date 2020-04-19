#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-19 16:08
@FilePath: /expdf/templates.py
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
    },
    line{
      stroke: black;
      stroke-width: 1px;
    }
    .assemble:hover circle{
      fill: white;
      stroke: black;
      stroke-width: 2px;
    }
    .assemble:hover line{
      stroke: black;
      stroke-width: 2px;
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


