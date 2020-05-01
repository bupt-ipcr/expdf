#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-30 22:40
@FilePath: /tests/test_extractor.py
@desc: 测试extractor中匹配效果
"""
from expdf.extractor import (
    Link,
    get_ref_title,
    get_urls,
    get_arxivs,
    get_dois,
    get_links
)


def test_get_ref_title():
    # 引号引用类型
    ref_1 = '''W. Jiang, G. Feng and S. Qin, “Optimal Cooperative Content Cachingand Delivery Policy for Heterogeneous Cellular Networks,” in IEEETransactions on Mobile Computing, vol. 16, no. 5, pp. 1382-1393, May2017.'''
    assert get_ref_title(ref_1) == 'Optimal Cooperative Content Cachingand Delivery Policy for Heterogeneous Cellular Networks,'
    
    # 分句引用类型
    ref_2 = '''L. Breslau, Pei Cao, Li Fan, G. Phillips, and S. Shenker. Web caching and zipf-like distributions: evidence and implications. In INFOCOM ’99. Eighteenth Annual Joint Conference of the IEEE Computer and Communications Societies. Proceedings. IEEE, volume 1, pages 126–134 vol.1, Mar 1999.'''
    assert get_ref_title(ref_2) == 'Web caching and zipf-like distributions: evidence and implications'
    
    ref_2_a = '''Abounadi, J., Bertsekas, D. and Borkar, V. S. (2001). Learning algorithms for Markov Decision  Processes with average cost. SIAM Journal on Control and Optimization, 40 681–698.'''
    assert get_ref_title(ref_2_a) == 'Learning algorithms for Markov Decision Processes with average cost'
    
    ref_2_b = '''Lowe, R., Wu, Y., Tamar, A., Harb, J., Abbeel, P. and Mordatch, I. (2017). Multi-agent actor-critic  for mixed cooperative-competitive environments. arXiv preprint arXiv:1706.02275.'''
    assert get_ref_title(ref_2_b) == 'Multi-agent actor-critic for mixed cooperative-competitive environments'
    
    ref_2_c = '''Macua, S. V., Tukiainen, A., Hern´andez, D. G.-O., Baldazo, D., de Cote, E. M. and Zazo, S. (2017). Di↵-dac: Distributed actor-critic for multitask deep reinforcement learning. arXiv preprint arXiv:1710.10363.'''
    assert get_ref_title(ref_2_c) == 'Di↵-dac: Distributed actor-critic for multitask deep reinforcement learning'
    
    ref_2_d = '''Littman, M. L. (2001). Value-function reinforcement learning in Markov games. Cognitive Systems Research, 2 55–66.'''
    assert get_ref_title(ref_2_d) == 'Value-function reinforcement learning in Markov games'
    
    ref_2_al = '''Mnih, V., Kavukcuoglu, K., Silver, D., Rusu, A. A., Veness, J., Bellemare, M. G., Graves, A., Riedmiller, M., Fidjeland, A. K., Ostrovski, G. et al. (2015). Human-level control through deep reinforcement learning. Nature, 518 529–533.'''
    assert get_ref_title(ref_2_al, strict=True) == 'Human-level control through deep reinforcement learning'
    
    # 暂时无法匹配的类型
    ref_3 = '''My title.: “123”, 1998'''
    assert get_ref_title(ref_3) == 'My title.: “123”, 1998'
    # strict mode
    
    assert get_ref_title(ref_1, strict=True) == 'Optimal Cooperative Content Cachingand Delivery Policy for Heterogeneous Cellular Networks,'
    assert get_ref_title(ref_2, strict=True) == 'Web caching and zipf-like distributions: evidence and implications'
    assert get_ref_title(ref_3, strict=True) is None


def test_get_urls():
    # 匹配所有url
    long_text = '''my first pdf: https://www.demo1.com/h3.pdf
                my second pdf: github.io/mypage/h4.html'''
    urls = get_urls(long_text)
    link1 = Link('pdf', 'https://www.demo1.com/h3.pdf', 'https://www.demo1.com/h3.pdf')
    link2 = Link('url', 'github.io/mypage/h4.html', 'github.io/mypage/h4.html')

    assert link1 in urls
    assert link2 in urls

    # 匹配仅有的url
    short_text = ''' bupt.edu.cn/xxx.pdf '''
    s_url = get_urls(short_text)[0]
    assert s_url.equal(Link('pdf', 'bupt.edu.cn/xxx.pdf', 'bupt.edu.cn/xxx.pdf'))

    # 如果没有url
    none_text = '''here is my sentence and contains no urls'''
    assert get_urls(none_text) == []


def test_get_arxivs():
    # 匹配描述格式的arxiv
    arxiv_text_1 = '''arXiv preprint arXiv:1312.5602, 2013.'''
    assert get_arxivs(arxiv_text_1)[0].equal(Link('arxiv', '1312.5602', 'https://arxiv.org/abs/1312.5602'))

    arxiv_text_2 = ''' arXiv.org.1511.0658'''
    assert get_arxivs(arxiv_text_2)[0].equal(Link('arxiv', '1511.0658', 'https://arxiv.org/abs/1511.0658'))

    arxiv_text_v1 = '''X. Zhang and L. Duan, “Optimal deployment of UAV net- works for delivering emergency wireless coverage,” 2017, arXIV:1710.05616v1.'''
    assert get_arxivs(arxiv_text_v1)[0].equal(Link('arxiv', '1710.05616v1', 'https://arxiv.org/abs/1710.05616v1'))

    # 匹配链接格式的arxiv
    arxiv_url = '''.. link is https://arxiv.org/abs/1812.02979 '''
    assert get_arxivs(arxiv_url)[0].equal(Link('arxiv', '1812.02979', 'https://arxiv.org/abs/1812.02979'))


def test_get_dois():
    # 匹配文本格式的DOI
    doi_text = '''Catalog IDs
    DOI: 10.1109/INFCOMW.2019.8845154
    ISBN: 9781728118789'''
    assert get_dois(doi_text)[0].equal(Link('doi', '10.1109/INFCOMW.2019.8845154', 'https://doi.org/10.1109/INFCOMW.2019.8845154'))

    # 匹配url格式的DOI
    doi_url = '''Demos·August 2019 · Pages 114-115 · https://doi.org/10.1145/3342280/3342327'''
    assert get_dois(doi_url)[0].equal(Link('doi', '10.1145/3342280/3342327', 'https://doi.org/10.1145/3342280/3342327'))


def test_get_links():
    test_text = '''
    my first pdf: https://www.demo1.com/h3.pdf
    arXiv preprint arXiv:1312.5602, 2013
    Demos·August 2019 · Pages 114-115 · https://doi.org/10.1145/3342280/3342327'''

    pdf_link = Link('pdf', 'https://www.demo1.com/h3.pdf', 'https://www.demo1.com/h3.pdf')
    arxiv_link = Link('arxiv', '1312.5602', 'https://arxiv.org/abs/1312.5602')
    doi_link = Link('doi', '10.1145/3342280/3342327', 'https://doi.org/10.1145/3342280/3342327')

    assert get_links(test_text) == [arxiv_link, doi_link, pdf_link]
