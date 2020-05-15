#!/usr/bin/env python
# coding=utf-8
"""
Parser of extend PDF file.

@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-05-15 15:31
@FilePath: /expdf/expdf/parser.py
"""
from io import BytesIO
from pathlib import Path
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
import requests
from .extractor import get_urls
from .processors import process_doc, process_pages, process_annots, process_text


class ExPDFParser:
    """ExPDFParser(uri="", local=False, strict=False)

    Enhanced infomations of a PDF object, includes title of the PDF,
    all kinds of links inside PDF content, citations listed in 
    `References`, info and metadate attribute of the PDF object.

    The parser is built on pdfminer to resolve PDF object, mainly
    use regex to extract links and citations from content of PDF.

    Parameters
    ----------
    uri : str
        Resource uri, local file location or a url.

    local : bool, default False, keyword only. 
        Set to True to force use local file.

    strict : bool, default False, keyword only. 
        Set to True to enable strict mode.
        In strict mode, if title cannot be found in a citation
        record, it will be ignored. If not in strict mode, complete
        citation will be returned as the title.

    Attributes
    ----------
    title : str
        Title of PDF.
        Title will be searched in info and metadate attribute of the
        PDF object, and if not found, it returns filename of uri.

    links : list
        Links in content of PDF.
        The parser use regex to extract links, and return it as a simple
        class `Link` with its type, uniform resource identifier and link.

    refs : list
        Citation titles list in `References` part of the PDF.
        The parser try to find out `References` part, seperate for each
        line, then use regex to extract paper title in the citation line.

    info : dict
        Attribute info of the PDF object.

    metadata : dict
        Attribute metadata of the PDF object.

    Examples
    --------
    Use ExPDFParser to resolve PDF.
    >>> from expdf import ExPDFParser
    >>> pdf = ExPDFParser("pdfs/test.pdf")
    >>> pdf.title
    'A Deep Learning Approach for Optimizing Content Delivering in Cache-Enabled HetNet'
    >>> for ref in pdf.refs:
    ...     print(f'- {ref}')
    ... 
    - Wireless caching: technical misconceptions and business barriers,
    - Optimal Cooperative Content Caching and Delivery Policy for Heterogeneous Cellular Networks,
    - Joint Caching, Routing, and Channel Assignment for Collaborative Small-Cell Cellular Net-works,
    - On the Complexity of Optimal Content Placement in Hierarchical Caching Networks,
    - Wireless Commun
    - Efﬁcient processing of deep neural networks: A tutorial and survey
    - Resource Man-agement with Deep Reinforcement Learning
    - Edge Caching at Base Stations with Device-to-Device Ofﬂoading
    - Optimal cell clustering and activation for energy saving in load-coupled wireless networks,
    - K. Murty, Linear programming, Wiley, 1983.
    - Minimum-Time Link Scheduling for Emptying Wireless Systems: Solution Characterization and Algorithmic Framework,

    """

    def __init__(self, uri, *, local=False, strict=False):
        """Initialize a parser with expend attributes of a PDF.

        Parameters
        ----------
        uri : str
            Resource uri, local file location or a url.

        local : bool, default False, keyword only. 
            Set to True to force use local file.

        strict : bool, default False, keyword only. 
            Set to True to enable strict mode.
            In strict mode, if title cannot be found in a citation
            record, it will be ignored. If not in strict mode, complete
            citation will be returned as the title.
        """
        filename, stream = get_stream(uri, local)
        expdf = ex_parser(stream, strict)
        expdf.update({
            'filename': filename
        })
        self._data = expdf

    @property
    def title(self):
        """Title of PDF"""
        info, metadata = self._data['info'], self._data['metadata']
        # try to get title from info attribute
        if 'Title' in info:
            title = info['Title']
            if isinstance(title, bytes):
                if title.decode('utf-8').strip():
                    return title.decode('utf-8').strip()
            else:
                if title.strip():
                    return title.strip()
        # try to get title from metadata attribute
        if 'dc' in metadata:
            if 'title' in metadata['dc'] and metadata['dc']['title']['x-default'].strip():
                return metadata['dc']['title']['x-default']

        # return filename when no title can be found
        return self._data['filename']

    @property
    def links(self):
        """list of inks in content of PDF."""
        return self._data['links']

    @property
    def refs(self):
        """list of citation titles list in `References` part of the PDF."""
        return self._data['refs']

    @property
    def info(self):
        """dict for attribute info of the PDF object."""
        return self._data['info']

    @property
    def metadata(self):
        """dict for attribute metadata of the PDF object."""
        return self._data['metadata']


def get_stream(uri, local=False):
    """Generate a byte stream from uri.

    For local file, open it as a byte stream. For network
    resource, get the resource and convert to byte stream.

    Parameters
    ----------
    uri : str
        Resource uri, local file location or a url.

    local : bool, default False
         Set to True to force use local file.

    Returns
    -------
    filename : str
        file name of PDF in the uri.

    stream : io.BytesIO
        bytes stream of PDF in uri.

    Raises
    ------
    FileNotFoundError
        raise when uri is a local file, and file was not found.
    """
    # find out whether uri is a url
    urls = get_urls(uri)
    local = local or not urls
    # if local is True, treat uri as local file anyway
    if local:
        path = Path(uri)
        if not path.exists():
            raise FileNotFoundError(f"Invalid local filename: {uri}")
        else:
            filename, stream = path.with_suffix('').name, path.open("rb")
    else:
        content = requests.get(uri).content
        filename, stream = uri.split("/")[-1], BytesIO(content)

    return filename, stream


def ex_parser(pdf_stream, password='', pagenos=[], maxpages=0):
    """Parser stream of a PDF, return dict of attributes.

    The parser use pdfminer to parse a PDF stream.

    The stream is converted to doc firstly, info and metadate are
    parsed from XMP metadata of doc. The doc will be process into
    a string text, by the way find annotates of PDF file, extract
    links from annotates.

    The text then will be processed with regex to find out links
    and citations, links will be append to links found in annotates
    and citations will be append to a list named refs.

    Parameters
    ----------
    pdf_stream : io.BytesIO-like
        pdf stream to be parsed.

    password : str, optional, default ''
        password of the PDF file.

    pagenos : list, optional, default []
        list of page numbers to be parsed.

    maxpages : int, optional, default 0
        max page number of the PDF file.

    Returns
    -------
    pdf_dict : dict
        dict of attributes of the PDF, includes:
        - text : text of PDF document.
        - info : info in XMP data of PDF file.
        - metadata : metadata in XMP data of PDF file.
        - links : links in PDF content and annotates.
        - refs : citations in part `References` of PDF.
    """

    # use pdfminer to resolve pdf stream
    parser = PDFParser(pdf_stream)
    doc = PDFDocument(parser, password=password, caching=True)

    # get info and metadata
    info, metadata = process_doc(doc)

    # get text of PDF, and get list of annotates
    text, annots_list, maxpage = process_pages(doc)

    links, refs = [], []

    # process annotates, find links
    for annots in annots_list:
        annots_links = process_annots(annots)
        if annots_links:
            links.extend(annots_links)

    # process text, find links and refs
    text_links, text_refs = process_text(text)

    links.extend(text_links)
    refs.extend(text_refs)

    pdf_dict = {
        'text': text,
        'info': info,
        'metadata': metadata,
        'links': links,
        'refs': refs
    }
    return pdf_dict
