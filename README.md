# ExPDF

## Overview

ExPDF is a tool that can generate citation relationship between PDFs, and create beautiful, interactive SVG figure inside Jupyter Notebook.  

![image](https://user-images.githubusercontent.com/38694199/81917751-2ef60000-9608-11ea-9c83-98f45010a5e7.png)

## Quickstart

With `Jupyter Notebook`, it is easy to visuzlize citation relationship between PDFs.  

Firstly, download and install by:

```bash
git clone https://github.com/bupt-ipcr/expdf
cd expdf
pip install ./
```

Secondly, use `expdf` to generate json file like:

```bash
expdf -d pdfs/ASV -o data.json
```

Finally, open `jupyter notebook` and try:

```python
  import json
  from expdf.visualize import create_fig
  with open('data.json', 'r') as f:
    data = json.load(f)
  fig = create_fig(data)
  fig
```

## Installation

download expdf with github and install it with pip

```bash
git clone https://github.com/bupt-ipcr/expdf
cd expdf
pip install ./
```

run `expdf -h` to see the help output:

```bash
usage: expdf [-h] [-a APPEND_PDF] [-r] [-o OUTPUT_DIR] PDF_PATH

Generate reference relation of all PDFs(given or inside PDF)

positional arguments:
  PDF_PATH              PDF path, or directory of PDFs if -r is used

optional arguments:
  -h, --help            show this help message and exit
  -a APPEND_PDF, --append APPEND_PDF
                        append a PDF file
  -d, --dir, --directory
                        treat PDF_PATH as a directory
  -e EXCLUDE_PDF, --exclude EXCLUDE_PDF
                        exclude a PDF file
  -o OUTPUT_DIR, -O OUTPUT_DIR, --output OUTPUT_DIR
                        output directory, default is current directory
  -v, --vis, --visualize
                        create a html file for visualize
  --vis-html HTML_FILENAME
                        output file name of html visualize
```

## Examples

simply use epdf like:

```bash
expdf pdfs/test.pdf
```

**Treat as a directory** with `-d` and it will scan all PDFs in specify directory:

```bash
expdf -d pdfs
```

**Append PDFs** with `-a`, since there may be sporadic papers not in the same folder:

```bash
expdf -d pdfs -a 1.pdf -a 2.pdf
```

**Exclude PDFs** with `-e`, to exclude some PDFs. Note that even if exclude pdf not exists,
there will be no error.

```bash
expdf -d pdfs -e test.pdf
```

To **specify output directory**, use `-o`, `-O` or `--output` like:

```bash
expdf pdfs/test.pdf -O ./urdir
```

To **generate visualize html file**, use `-v` and `--vis-html` like:

```bash
expdf -r pdfs/ASV -v --vis-html='vis.html'
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

- `PDFNode`

  `PDFNode` is a class that maintain a dict of all its instances. Two PDF that have same title(or just have difference in punctuations) will point to same node.
  `LocalPDFNode` is a subclass of `PDFNode`, which enables you to modify references of a PDF.

  usually it is used with parser like:

  ````python
  from expdf import ExPDFParser, LocalPDFNode
  
  expdf_parser = ExPDFParser("tests/test.pdf")
  localPDFNode = LocalPDFNode(expdf_parser.title, expdf_parser.refs)
  pdf_info = PDFNode.get_json()
  print(pdf_info)
  ````

  otherwise, you can also assign title and refs without parser(maybe human is more precise than parser and regex expressions), just like:

  ```python
  from expdf.graph import PDFNode, LocalPDFNode
  
  # just a example, we wwill never see title like this
  LocalPDFNode('title0', refs=['title1', 'title2'])
  LocalPDFNode('title1', refs=['title3'])
  LocalPDFNode('title2', refs=['title3'])
  pdf_info = PDFNode.get_json()
  print(pdf_info)
  ```

- `visualize`

  PDFNode give you infos of PDFs, such as citation relationship(show as parents and children). But why not visualize it?

  `visuzlize` provides a top-level function `create_fig` built on `networkx`, `plotly`. `networkx` provedes methods to  allocate positions
  of all nodes and `plotly` is a powerful visualization tool.

  `render` invokes `create_fig` and write it into html file.

  Visualize is recommended to be use inside `jupyter notebook`, since plotly only support events(click, hover, etc) with it.  You can use like:

  ```bash
  expdf -d pdfs/ASV -o data.json
  ```

  ```python
  # in your jupyter notebook
  import json
  from expdf.visualize import create_fig
  with open('data.json', 'r') as f:
    data = json.load(f)
  fig = create_fig(data)
  fig
  ```

  You can also save it as html, just like:

  ```bash
  expdf -d pdfs/ASV -o data.json -v --vis-html=vis.html
  ```

## Various

- Author: Jiawei Wu <13260322877@163.com>
- License: MIT
