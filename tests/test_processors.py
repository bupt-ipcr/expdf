#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-05-01 19:16
@FilePath: /tests/test_processors.py
@desc: 测试
"""

from expdf.processors import (
    process_text
)


def test_process_text_refs():
    """测试Process_text的refs是否正确"""
    text_1 = '''
References
[1] G. Paschos, E. Bastug, I. Land, G. Caire and M. Debbah, “Wireless
caching: technical misconceptions and business barriers,” in IEEE Com-
munications Magazine, vol. 54, no. 8, pp. 16-22, Aug. 2016.

[2] W. Jiang, G. Feng and S. Qin, “Optimal Cooperative Content Caching
and Delivery Policy for Heterogeneous Cellular Networks,” in IEEE
Transactions on Mobile Computing, vol. 16, no. 5, pp. 1382-1393, May
2017.

[3] A. Khreishah, J. Chakareski and A. Gharaibeh, “Joint Caching, Routing,
and Channel Assignment for Collaborative Small-Cell Cellular Net-
works,” in IEEE Journal on Selected Areas in Communications, vol. 34,
no. 8, pp. 2275-2284, Aug. 2016.

[4] K. Poularakis and L. Tassiulas, “On the Complexity of Optimal Content
Placement in Hierarchical Caching Networks,” in IEEE Transactions on
Communications, vol. 64, no. 5, pp. 2092-2103, May 2016.

[5] L. Lei, D. Yuan, C. K. Ho, and S. Sun, “A uniﬁed graph labeling
algorithm for consecutive-block channel allocation in SC-FDMA, IEEE
Trans. Wireless Commun., vol. 12, no. 11, pp. 5767-5779, Nov. 2013

[6] V. Sze, Y. Chen, T. Yang, and J. Emer, “Efﬁcient processing of deep
neural networks: A tutorial and survey”, http://arxiv.org/abs/1703.09039,
Mar. 2017.

[7] H. Mao, M. Alizadeh, I. Menache, and S. Kandula. “Resource Man-
agement with Deep Reinforcement Learning”, In Proceedings of the 15th
ACM Workshop on Hot Topics in Networks (HotNets). ACM, New York,
USA, 50-56, 2016.

[8] W. Wang, R. Lan, J. Gu, A. Huang, H. Shan, Z. Zhang, “Edge Caching at
Base Stations with Device-to-Device Ofﬂoading”, in IEEE Access, vol.PP,
no.99, pp.1-1

[9] L. Lei, D. Yuan, C. K. Ho, and S. Sun, “Optimal cell clustering and
activation for energy saving in load-coupled wireless networks,” in IEEE
Transactions on Wireless Communications, vol. 14, no. 11, pp. 6150–
6163, Nov. 2015.

[10] K. Murty, Linear programming, Wiley, 1983.
[11] V. Angelakis, A. Ephremides, Q. He and D. Yuan, “Minimum-Time Link
Scheduling for Emptying Wireless Systems: Solution Characterization
and Algorithmic Framework,” in IEEE Transactions on Information
Theory, vol. 60, no. 2, pp. 1083-1100, Feb. 2014.

453
    '''

    _, refs_1 = process_text(text_1)
    assert refs_1 == [
        'Wireless caching: technical misconceptions and business barriers,',
        'Optimal Cooperative Content Caching and Delivery Policy for Heterogeneous Cellular Networks,',
        'Joint Caching, Routing, and Channel Assignment for Collaborative Small-Cell Cellular Net-works,',
        'On the Complexity of Optimal Content Placement in Hierarchical Caching Networks,',
        'Wireless Commun',
        'Efﬁcient processing of deep neural networks: A tutorial and survey',
        'Resource Man-agement with Deep Reinforcement Learning',
        'Edge Caching at Base Stations with Device-to-Device Ofﬂoading',
        'Optimal cell clustering and activation for energy saving in load-coupled wireless networks,',
        'K. Murty, Linear programming, Wiley, 1983.',
        'Minimum-Time Link Scheduling for Emptying Wireless Systems: Solution Characterization and Algorithmic Framework,'
    ]
