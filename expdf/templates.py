#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-28 12:14
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
    .bold{
      stroke: black;
      stroke-width: 2px;
    }
    .slim{
      stroke: black;
      stroke-width: 1px;
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
    <script language='JavaScript'>
    var selectedLines = [];
    function boldenLines(e){
      title = e.srcElement.getAttribute('title')
      var lines = document.getElementsByTagName('line');
      var line;
      for (var i = 0; i < lines.length; i++) {
        line = lines[i];
        if(line.getAttribute('start') == title || line.getAttribute('end') == title){
          line.setAttribute("class", 'bold');
          selectedLines.push(line);
        }
      }
    }
    function slimLines(e){
      for (var i = 0; i < selectedLines.length; i++) {
        line = selectedLines[i];
        line.setAttribute("class", 'slim');
      }
      selectedLines = [];
    }
    function addMouseEvent() {
      var circles = document.getElementsByTagName('circle');
      var circle;
      for (var i = 0; i < circles.length; i++) {
        circle = circles[i];
          circle.addEventListener('mouseover', boldenLines, true)
          circle.addEventListener('mouseout', slimLines, true)
      }
    }
    window.addEventListener('load', addMouseEvent, true);
    </script>
  </head>
  <body>
    <div style="margin:100px">
    SVG_CONTENT
    </div>
  </body>
</html>
'''
