#!/usr/bin/env python
# coding=utf-8
"""
Define node that contains basic infomation of PDF and citation 
relationship between PDFs.

@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-05-15 16:20
@FilePath: /expdf/expdf/pdfnode.py
"""
import json
import logging
import re


class PDFNode:
    """PDFNode('title0', ['title1', 'title2'])

    A PDFNode is a node that represents a PDF, use title of the
    PDF as unique identifier. In particular, since citations to
    the same PDF may be different, such as typo error, PDFNode
    use numbers and letters(i.e. \w in regex) and lower them to
    consist unique key of a node.

    To ensure uniqueness of PDFNodes, the class maintains a 
    dictionary about all instances, with unique key as key and 
    instance as value.

    When a PDFNode instance is created, parameter refs specified
    citations fo the node. Since a title corresponds to a unique
    key and a key corresponds to a unique PDFNode instance, refs
    can convert into a set of PDFNodes. Nonexists PDFNode will be
    create.

    Parameters
    ----------
    title : str
        title of the PDF.

    refs : list
        a list of titles of cited PDFs of the PDF.

    Examples
    --------
    Create a PDFNode instance, create non-exists PDFNodes in refs.
    >>> node = PDFNode('title0', ['title1', 'title2'])
    >>> node.title
    'title0'
    >>> node.actients
    {<expdf.pdfnode.PDFNode object at 0x11da5e7d0>, <expdf.pdfnode.PDFNode object at 0x11da5ea50>}

    Get all instances of PDFNode.
    >>> node = PDFNode('title0', ['title1', 'title2'])
    >>> PDFNode.nodes()
    [<expdf.pdfnode.PDFNode object at 0x11da5e790>, <expdf.pdfnode.PDFNode object at 0x11da5e7d0>, <expdf.pdfnode.PDFNode object at 0x11da5ea50>]

    Clear all instances.
    >>> node = PDFNode('title0', ['title1', 'title2'])
    >>> PDFNode.clear_nodes()
    >>> PDFNode.nodes()
    []

    Call PDFNode() to get already exists node instance.
    >>> PDFNode('title0', ['title1', 'title2'])
    <expdf.pdfnode.PDFNode object at 0x11da5ec90>
    >>> node = PDFNode('title0', ['title1', 'title2'])
    >>> node
    <expdf.pdfnode.PDFNode object at 0x11da5ec90>
    >>> node = PDFNode('title0')
    >>> node
    <expdf.pdfnode.PDFNode object at 0x11da5ec90> 

    Specify different refs when getting an exist node instance
    result in error.
    >>> PDFNode('title0', ['title1', 'title2'])
    <expdf.pdfnode.PDFNode object at 0x11da5ec90>
    >>> node = PDFNode('title0', ['title1', 'title3'])
    Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
    File "/Users/yunfeng/Downloads/expdf/expdf/pdfnode.py", line 35, in __new__

    TypeError: Can't instantiate PDFNode with same title but different refs

    Raises
    ------
    TypeError: Can't instantiate PDFNode with same title but different refs
        Specify different refs when getting an exist node instance
        result in error.

    See Also
    --------
    LocalPDFNode

    Notes
    -----
    Refs, i.e. actients, is designed immutable, and will raise 
    TypeError if two call of PDFNode point to same key and different
    refs. To change the attribute, use method `set_refs`.
    """
    instances = {}

    def __new__(cls, title, refs=None):
        """Create new PDFNode instance, or get one if key exists.

        An instance of PDFNode use sub of title as key. If key exists,
        check whether two refses are corrspond. If key not exists, 
        create a instance and record it in instances.

        Parameters
        ----------
        title : str
            title of the PDF.

        refs : list
            a list of titles of cited PDFs of the PDF.
        """
        node_key = re.sub(r'\W', '', title.lower())
        if node_key in cls.instances:
            obj = cls.instances[node_key]

            logging.info('get', title, obj.actients)

            if refs is None or {actient.title for actient in obj.actients} == set(refs):
                return obj
            else:
                raise TypeError(
                    "Can't instantiate PDFNode with same title but different refs")
        else:
            obj = object.__new__(cls)
            cls.instances[node_key] = obj

            # assignments for new instance
            obj.node_key = node_key
            obj.title, obj.local_file = title, False
            obj.parents, obj.children = set(), set()
            obj.posterities = set()
            obj.actients = {PDFNode(ref)
                            for ref in refs} if refs is not None else set()
            for node in obj.actients:
                node.posterities.add(obj)

            logging.info('create', title, obj.actients)

            return obj

    @classmethod
    def nodes(cls):
        """Return list of instances."""
        return list(cls.instances.values())

    @classmethod
    def clear_nodes(cls):
        """Clear all instances."""
        cls.instances.clear()

    @classmethod
    def get_json(cls):
        """Get infomations of all PDFNodes as a json object."""
        nodes = []
        for pdf_node in cls.nodes():
            node = {
                'node_key': pdf_node.node_key,
                'title': pdf_node.title,
                'local': pdf_node.local_file,
                'actients': [
                    {
                        'node_key': actient.node_key,
                        'title': actient.title
                    }
                    for actient in pdf_node.actients
                ],
                'posterities': [
                    {
                        'node_key': posterity.node_key,
                        'title': posterity.title
                    }
                    for posterity in pdf_node.posterities
                ]
            }
            nodes.append(node)

        return json.dumps(nodes)

    def set_refs(self, refs):
        """method to set refs"""
        self.actients = {PDFNode(ref)
                         for ref in refs} if refs is not None else set()
        for node in self.actients:
            node.posterities.add(self)


class LocalPDFNode(PDFNode):
    """Subclass of PDFNode that allow override of refs.

    When a node of PDF is created, the refs is assigned.
    However, if the node corrspond to a local file, it
    may be create because of citation point to it, and
    when create the node without awareness of its exist,
    it cause error.

    Thus, we use a subclass of PDFNode to allow override
    refs in process of new a PDFNode instance.
    """
    def __new__(cls, title, refs=None):
        """new a instance and allow override refs"""
        obj = PDFNode(title)
        obj.local_file = True
        if refs is not None:
            obj.set_refs(refs)
        return obj
