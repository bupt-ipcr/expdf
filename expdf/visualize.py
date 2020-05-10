#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@author: Jiawei Wu
@create time: 2020-05-08 17:05
@edit time: 2020-05-10 10:50
@FilePath: /expdf/expdf/visualize.py
@desc: 
"""

import networkx as nx
import plotly.graph_objects as go
import json


def create_digraph(data):
    DG = nx.DiGraph()
    # add nodes
    for index, node in enumerate(data):
        DG.add_node(node['node_key'], title=node['title'], local=node['local'],
                    actients=node['actients'], posterities=node['posterities'], index=index, highlight=False)

    # add edges
    for node in data:
        for actient in node['actients']:
            DG.add_edge(node['node_key'], actient['node_key'])

    # get pos
    pos_dict = nx.drawing.layout.fruchterman_reingold_layout(DG)
    # set pos
    for node, pos in pos_dict.items():
        DG.nodes[node]['pos'] = pos

    return DG


def create_edge_trace(DG):
    # edge trace data
    edge_trace_x, edge_trace_y = [], []
    for edge in DG.edges():
        x0, y0 = DG.nodes[edge[0]]['pos']
        x1, y1 = DG.nodes[edge[1]]['pos']
        edge_trace_x.extend([x0, x1, None])
        edge_trace_y.extend([y0, y1, None])

    # create trace
    edge_trace = go.Scatter(
        x=edge_trace_x, y=edge_trace_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')
    return edge_trace


def create_node_trace(DG):
    # node trace data
    node_trace_x, node_trace_y = [], []
    for index, node_key in enumerate(DG.nodes()):
        x, y = DG.nodes[node_key]['pos']
        node_trace_x.append(x)
        node_trace_y.append(y)

    # create trace
    node_trace = go.Scatter(
        x=node_trace_x, y=node_trace_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            reversescale=True,
            color=[],
            size=[],
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line=dict(
                width=2,
                color=[]
            )))

    node_adjacencies = [len(adjacencies[1]) for adjacencies in DG.adjacency()]
    node_text = [DG.nodes[node]['title'] for node in DG.nodes()]
    node_marker_line_color = ['black'] * DG.number_of_nodes()

    node_trace.text = node_text.copy()
    node_trace.marker.color = node_adjacencies.copy()
    node_trace.marker.size = [10] * len(node_adjacencies)
    node_trace.marker.line.color = node_marker_line_color.copy()

    return node_trace


def create_fig(data):
    # create DG
    DG = create_digraph(data)
    # create fig
    edge_trace, node_trace = create_edge_trace(DG), create_node_trace(DG)
    fig = go.FigureWidget(data=[edge_trace, node_trace],
                          layout=go.Layout(
        title='<br>Network graph made with Python',
        titlefont_size=16,
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
    )

    # click event
    node_keys = [node for node in DG.nodes()]
    node_marker_line_color = ['black'] * DG.number_of_nodes()
    hflag = False

    def highlight(trace, points, state):
        lc = list(trace.marker.line.color)
        for idx in points.point_inds:
            point_node_key = node_keys[idx]
            # get all nodes
            associate_nodes = DG.nodes[point_node_key]['actients'] + DG.nodes[point_node_key]['posterities']
            associate_nodes = [associate_node['node_key'] for associate_node in associate_nodes]
            associate_nodes.append(point_node_key)
            for associate_node in associate_nodes:
                # change color
                node_index = DG.nodes[associate_node]['index']
                lc[node_index] = 'orange'
        with fig.batch_update():
            trace.marker.line.color = lc

    def un_highlight(trace, points, state):
        with fig.batch_update():
            trace.marker.line.color = node_marker_line_color.copy()

    def change_highlight(trace, points, state):
        nonlocal hflag
        if hflag:
            hflag = False
            un_highlight(trace, points, state)
        else:
            hflag = True
            highlight(trace, points, state)

    fig.data[1].on_click(change_highlight)
    return fig


def render(data, filename):
    fig = create_fig(data)
    with open(filename, 'w') as f:
        fig.write_html(file=f)