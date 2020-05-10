#!/usr/bin/env python
# coding=utf-8
"""
Generate citation relationship between PDFs, and visualize it.

Features

* Extract references from PDF
@FilePath: /expdf/expdf/__init__.py
* Work on HTML and Jupyter notebook
* Use as command-line tool or Python package

Usage

* Use as command-line tool `expdf`
Command-line tool supports generate json file and HTML visualize file.

* Use as Python Package `import expdf`
>>> from expdf import ExPDFParser
>>> pdf = ExPDFParser("tests/test.pdf")
>>> print('title: ', pdf.title)
>>> print('info: ', pdf.info)
>>> print('metadata: ', pdf.metadata)
>>> 
>>> print('Refs: ')
>>> for ref in pdf.refs:
...     print(f'- {ref}')

* Use in jupyter notebook with generated json file
import json
from expdf.visualize import create_fig
with open('data.json', 'r') as f:
data = json.load(f)
fig = create_fig(data)
fig

Copyright (c) 2020, Jiawei Wu <13260322877@163.com>
License: MIT
"""

from .pdfnode import LocalPDFNode, PDFNode
from .visualize import render
from .parser import ExPDFParser
