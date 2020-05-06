# ExPDF

## Overview

ExPDF is a tool that can generate citation relationship between PDFs. 

Based on pdfminer, expdf use SVG to visualize. 

## Installation

download expdf with github and install it with pip

```bash
git clone https://github.com/bupt-ipcr/expdf
cd expdf
pip install expdf
```

run `expdf -h` to see the help output:

```bash
usage: expdf [-h] [-a APPEND_PDF] [-r] [-o OUTPUT_DIR] PDF_PATH

Generate reference relation of all PDFs(given or inside PDF)

positional arguments:
  PDF_PATH              PDF path, or directory of PDFs if -r is used

optional arguments:
  -h, --help            show this help message and exit
  -a APPEND_PDF         append a PDF file
  -r, --recursive       treat PDF_PATH as a directory
  -o OUTPUT_DIR, -O OUTPUT_DIR, --output OUTPUT_DIR
                        output directory, default is current directory
```

## Examples

simply use epdf like:

```bash
expdf tests/test.pdf
```

**Treat as a directory** with `-r` and it will scan all PDFs in specify directory:

```bash
expdf -r tests
```

**Append PDFs** with `-a`, since there may be sporadic papers not in the same folder:

```bash
expdf -r tests -a 1.pdf -a 2.pdf
```

To **specify output directory**, use `-o`, `-O` or `--output` like:

```bash
expdf expdf/tests/test.pdf -O ./urdir
```

## Usage as Python library

Here we have three main parts of expdfs: `ExPDFParser`, `Graph` and `render`.

- `ExPDFParser`

  a parser built top on pdfminer, look for metadata, links and references of a PDF file.

  ```python
  # ensure you have ./tests/test.pdf
  from expdf import ExPDFParser
  pdf = ExPDFParser("tests/test.pdf")
  print('title: ', pdf.title)
  print('info: ', pdf.info)
  print('metadata: ', pdf.metadata)
  
  print('Links: ')
  for link in pdf.links:
    print(f'- {link}')

  print('Refs: ')
  for ref in pdf.refs:
    print(f'- {ref}')
  ```

- `Graph`

  the Graph is base on a class that maintain a dict of all its instances, `PDFNode`. Two PDF that have same title(or just have difference in punctuations) will point to same node.

  usually Graph is used with parser like:

  ````python
  from expdf import ExPDFParser, LocalPDFNode, Graph
  
  expdf_parser = ExPDFParser("tests/test.pdf")
  localPDFNode = LocalPDFNode(expdf_parser.title, expdf_parser.refs)
  graph = Graph()
  graph.calculate()
  print(graph.infos)
  ````

  however, you can also assign title and refs without parser(maybe human is more precise than parser and regex expressions), just like:

  ```python
  from expdf.graph import PDFNode, LocalPDFNode, Graph
  
  # just a example, we wwill never see title like this
  LocalPDFNode('title0', refs=['title1', 'title2'])
  LocalPDFNode('title1', refs=['title3'])
  LocalPDFNode('title2', refs=['title3'])
  graph = Graph()
  graph.calculate()
  print(graph.infos)
  ```

- `render`

  Graph give you infos of PDFs, such as citation relationship(show as parents and children). But why not visualize it?

  ```bash
  from expdf.graph import LocalPDFNode, Graph
  from expdf.visualize import render
  from expdf.parser import ExPDFParser
  
  expdf_parser = ExPDFParser("tests/test.pdf")
  localPDFNode = LocalPDFNode(expdf_parser.title, expdf_parser.refs)
  graph = Graph()
  graph.calculate()
  render(graph.infos, 'svg.html')
  ```

  then you can open svg.html in browser.

## Various

- Author: Jiawei Wu <13260322877@163.com>
- License: MIT
