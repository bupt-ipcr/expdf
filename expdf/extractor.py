#!/usr/bin/env python
# coding=utf-8
"""
Module of extractors, to get special infomations out.

@author: Jiawei Wu
@edit time: 2020-05-15 15:31
@FilePath: /expdf/expdf/extractor.py
"""
import re
__all__ = ['get_ref_title', 'get_links', 'get_urls']


class Link:
    """Link(linktype='', uri='', link='')

    A simple class to record a link (find in a PDF file),
    infomations include type of link, uniform resource identifier
    of the link(specify by link type) and the complete link.

    Parameters
    ----------
    linktype : str, typically in ['doi', 'arxiv', 'pdf', 'url']
        linktype is type of the link, 'doi' means a doi link,
        'arxiv' means a arxiv link, 'pdf' means a url end with 
        'pdf' and 'url' means a normal link.

    uri : str, uniform resource identifier of a link
        for doi: doi reference location
        for arxiv: serial number with dot of an arxiv paper
        for pdf: the url
        for url: the url

    link : str, complete link of a link
        link of a Link instance should be unique.

    Notes
    -----
    class Link will not check whether attribute link is corrspond to 
    linktype and uri.

    Examples
    --------
    Create a Link instance.
    >>> link = Link('arxiv', '1312.5602', 'https://arxiv.org/abs/1312.5602')

    Check whether two Link instance is same at link, ignoring difference
    in 'http' and 'https'.
    >>> link1 = Link('arxiv', '1312.5602',
    ... 'https://arxiv.org/abs/1312.5602')
    >>> link2 = Link('url', 'https://arxiv.org/abs/1312.5602',
    ... 'https://arxiv.org/abs/1312.5602')
    >>> link1.equal(link2)
    >>> link1 == link2
    True

    Strickly check whether two Link instance is equal.
    >>> link1 = Link('arxiv', '1312.5602',
    ... 'https://arxiv.org/abs/1312.5602')
    >>> link2 = Link('url', 'https://arxiv.org/abs/1312.5602',
    ... 'https://arxiv.org/abs/1312.5602')
    >>> link1.equal(link2)
    False
    """

    def __init__(self, linktype, uri, link):
        """Initialize a link with attributes of a link

        Parameters
        ----------
        linktype : str, typically in ['doi', 'arxiv', 'pdf', 'url']
            linktype is type of the link, 'doi' means a doi link,
            'arxiv' means a arxiv link, 'pdf' means a url end with 
            'pdf' and 'url' means a normal link.

        uri : str, uniform resource identifier of a link
            for doi: doi reference location
            for arxiv: serial number with dot of an arxiv paper
            for pdf: the url
            for url: the url

        link : str, complete link of a link
            link of a Link instance should be unique.

        Examples
        --------
        >>> link = Link('arxiv', '1312.5602', 'https://arxiv.org/abs/1312.5602')    
        """
        self.linktype, self.uri, self.link = linktype, uri, link

    def __eq__(self, other):
        """Return self==value by compare attribute link.

        Difference between 'http' and 'https' will be ignored, 
        method returns True even linktype and uri are not the same.
        """
        return self.link == other.link or self.link.replace('https', 'http') == other.link.replace('https', 'http')

    def equal(self, other):
        """Strictly defined equal between self and other Link instance.

        Only if two Link instances have same linktype, uri and link, 
        they are equal.
        """
        return self.uri == other.uri and self.linktype == other.linktype and self.link == other.link


def get_ref_title(ref_text, *, strict=False):
    """Get title of an reference from text of it.

    Try to matching with different special regex expression,
    return matched content. If failed in matching, return 
    complete ref_text as title if strict mode is off, or return
    None.

    Parameters
    ----------
    ref_text : str, a string that contains(may contains) citation.
        ref_text is usually matched by other rule such as regex
        expression, it contains text of a citation in the paper,
        or may not.

    strict : bool, keyword only, set to True to open strict mode.
        In strict mode, ref_text that match none of regex expressions
        will return None, instand of ref_text it self.

    Returns
    -------
    ref_title : str, title of citation find in reference text
    """
    # pre process
    ref_text = ref_text.replace('- ', '-').replace('  ', ' ')
    # tail re
    tail_re = r'in|arxiv|doi|journal|IEEE|\w+com|press|nature|\d+[–-]\d+'
    # e.g. W. Jiang, G. Feng and S. Qin, “Optimal Cooperative Content Cachingand Delivery Policy for Heterogeneous Cellular Networks,” in IEEETransactions on Mobile Computing, vol. 16, no. 5, pp. 1382-1393, May2017.
    quote_re = rf'''([^“]+)[,.]?\s*“(.+)”.*({tail_re})'''
    if re.search(quote_re, ref_text, re.I):
        return re.search(quote_re, ref_text, re.I).groups()[1]

    # e.g. L. Breslau, Pei Cao, Li Fan, G. Phillips, and S. Shenker. Web caching and zipf-like distributions: evidence and implications. In INFOCOM ’99. Eighteenth Annual Joint Conference of the IEEE Computer and Communications Societies. Proceedings. IEEE, volume 1, pages 126–134 vol.1, Mar 1999.
    dot_re = r'''.+?(?<!.{4}[A-Z]|et al)\.\s*([()0-9]\.)?\s*([^.]+?[^A-Z])\.(.+)$'''  # note: cannot use re.I here
    if re.search(dot_re, ref_text):
        # dot_re limits too loose, use tail_re as supplement
        groups = re.search(dot_re, ref_text).groups()
        if not strict or re.search(tail_re, groups[2], re.I):
            return groups[1]

    if strict:
        return None
    return ref_text


def get_urls(text):
    """Extract urls from text.

    Parameters
    ----------
    text : text that contains url(s)

    Returns
    -------
    links : a list of Links of urls in the text.
    """
    # URL
    URL_REGEX = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""

    links = []
    for url in set(re.findall(URL_REGEX, text, re.I)):
        if url.lower().endswith('pdf'):
            links.append(Link('pdf', url, url))
        else:
            links.append(Link('url', url, url))
    return links


def get_arxivs(text):
    """Extract arxivs from text.

    Parameters
    ----------
    text : text that contains arxiv(s)

    Returns
    -------
    links : a list of Links of arxivs in the text.
    """
    re_texts = [r"""arxiv:\s?([^\s,]+)""", r"""arXiv\.org\.\s?([^\s,]+)"""]
    re_url = r"""arxiv.org/abs/([^\s,]+)"""
    arxivs = []
    for re_text in re_texts:
        arxivs.extend(re.findall(re_text, text, re.I))
    arxivs.extend(re.findall(re_url, text, re.I))

    links = [Link('arxiv', arxiv, f'https://arxiv.org/abs/{arxiv}')
             for arxiv in set([r.strip(".") for r in arxivs])]
    return links


def get_dois(text):
    """Extract dois from text.

    Parameters
    ----------
    text : text that contains doi(s)

    Returns
    -------
    links : a list of Links of dois in the text.
    """
    re_text = r"""DOI:\s?([^\s,]+)"""
    re_url = r'''https?://doi.org/([^\s,]+)'''

    dois = []
    dois.extend(re.findall(re_text, text, re.I))
    dois.extend(re.findall(re_url, text, re.I))
    links = [Link('doi', doi, f'https://doi.org/{doi}')
             for doi in set([r.strip(".") for r in dois])]
    return links


def get_links(text):
    """Extract all kind of links from text.

    Ordanaty get arxivs, dois and urls from text.
    Link of type doi and arxiv will never have same link,
    but when extract urls, all of returned links will be
    checked to ensure no repeat links.


   Parameters
    ----------
    text : text that contains doi(s)

    Returns
    -------
    links : a list of Links of all kinds.
    """
    links = []
    # for arxivsd and dois
    links.extend(get_arxivs(text))
    links.extend(get_dois(text))
    # repeat check for urls
    for link in get_urls(text):
        if link not in links:
            links.append(link)

    return links
