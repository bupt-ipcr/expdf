#!/usr/bin/env python
# coding=utf-8
"""
@author: Jiawei Wu
@create time: 1970-01-01 08:00
@edit time: 2020-04-19 16:38
@FilePath: /caoxiaojing/expdf/expdf/visualize.py
@desc: 可视化PDF关系
"""
from .templates import svg_template
R = 30   # 圆的半径
W = 4 * R  # 圆的间距
H = 3 * R    # 行间距


def infos_to_data(infos):
    """将infos转换为render需要的格式"""
    data = {
        'groups': {}
    }
    for gid, gcontent in enumerate(infos):
        group = {}
        circle_dict = {}
        # 获取group对应的画幅
        levels, min_level = gcontent['levels'], gcontent['min_level']
        max_nodes = max(len(nodes) for level, nodes in levels.items())
        width, height = max_nodes + 1, abs(min_level) + 1

        group['width'], group['height'] = width, height

        circles, lines = {}, []
        # 获取每个circle的属性与每个line的属性
        for level, nodes in levels.items():
            # 获取上层nodes
            pres = levels.get(level+1, [])
            # 遍历这一层nodes
            n_nodes = len(nodes)
            for order, node in enumerate(nodes):
                # 确定每个circle属性
                circle = {
                    'x': order - n_nodes / 2 + width / 2,
                    'y': abs(level) + 1,
                    'title': node['title'],
                    'local': node['local_file']
                }
                circles[node['title']] = circle

                # 确定所有相关的线
                for pre in pres:
                    if node['title'] in pre['children_titles']:
                        line = {
                            'x1': circles[pre['title']]['x'],
                            'y1': circles[pre['title']]['y'],
                            'x2': circle['x'],
                            'y2': circle['y'],
                            'start': pre['title'],
                            'end': node['title'],
                        }
                        lines.append(line)

        group['circles'] = list(circles.values())
        group['lines'] = lines
        data['groups'][gid] = group
    return data


def create_lines_html(lines):
    lines_template = '''<g>
    {}
    </g>'''
    line_template = '''<line class="link" x1="{}" y1="{}" x2="{}" y2="{}" start="{}" end="{}"></line>'''
    line_htmls = (line_template.format(l['x1'] * W, l['y1'] * H, l['x2']
                                       * W, l['y2'] * H, l['start'], l['end']) for l in lines)
    join_html = '      \r\n'.join(line_htmls)
    lines_html = lines_template.format(join_html)
    return lines_html


def create_circles_html(circles):
    circles_template = '''<g>
    {}
    </g>'''
    circle_template = '''
      <g class="node" transform="translate({}, {})" style="fill: white;">
        <circle class="{}" r="{}" title="{}"></circle>
        <text class="nodeLabel" transform="translate({}, {})">{}</text>
      </g>
    '''
    circle_htmls = (circle_template.format(
        circle['x'] * W, circle['y'] * H, 'local' if circle['local'] else 'nonlocal', R, circle['title'], -W/4, -H/2, circle['title']) for circle in circles)
    join_html = '      \r\n'.join(circle_htmls)
    circles_html = circles_template.format(join_html)
    return circles_html


def create_group_html(item_htmls, offset):
    group_template = '''
    <g transform="translate({}, 0)">
        {}
    </g>
    '''
    join_html = '    \r\n'.join(item_htmls)
    group_html = group_template.format(offset * W, join_html)
    return group_html


def create_svg_html(group_htmls, max_height):
    svg_template = '''<svg width="100%" height="{}px" pointer-events="all" xmlns="http://www.w3.org/2000/svg" version="1.1">
    {}
    </svg>
    '''
    join_html = '\r\n'.join(group_htmls)
    svg_html = svg_template.format((max_height + 2) * H, join_html)
    return svg_html


def gererate_svg(data):
    groups = data['groups']
    offset = 1
    max_height = 0
    group_htmls = []
    for gid, group in groups.items():
        lines, circles = group['lines'], group['circles']
        lines_html = create_lines_html(lines)
        circles_html = create_circles_html(circles)
        group_html = create_group_html([lines_html, circles_html], offset)
        offset += group['width']
        max_height = max(max_height, group['height'])
        group_htmls.append(group_html)
    svg_html = create_svg_html(group_htmls, max_height)
    html = svg_template
    html = html.replace('SVG_CONTENT', svg_html)
    return html


def render(infos):
    """接口"""
    return gererate_svg(infos_to_data(infos))
