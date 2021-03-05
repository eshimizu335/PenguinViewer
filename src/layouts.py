import dash_core_components as dcc
import dash_html_components as html
import dash_cytoscape as cyt
import pandas as pd

import json

import read

skip_switch_list = []  # cdp読み込みの際に既出スイッチは飛ばす
core_info_list = read.get_core_information()
node_info_list = read.read_cdp(core_info_list[2], skip_switch_list)

type_list = []
mode_list = []

for i in range(len(node_info_list[0])):
    # 物理ポート情報の取得
    c_type = read.get_cable_type(node_info_list[0][i], node_info_list[2][i])
    type_list.append(c_type)
    # ポートモード情報の取得
    p_mode = read.get_port_info(node_info_list[0][i], node_info_list[2][i])
    mode_list.append(p_mode)

# cdpの出力はインターフェース名にスペース入ってるのでreplaceで消す
src_int = str(node_info_list[2]).replace(' ', '')
dst_int = str(node_info_list[3]).replace(' ', '')

# ノードとエッジの変数の作成(物理図と論理図で共用)
core_primary = core_info_list[0]
core_secondary = core_info_list[1]
from_node = node_info_list[0]
to_node = node_info_list[1]
srcport = node_info_list[2]
dstport = node_info_list[3]

# fromとtoを持つedgeのデータフレームおよびnodesを物理図用(p)、論理図用(l)それぞれ作成
edges_p = pd.DataFrame.from_dict(
    {'from': from_node, 'to': to_node, 'srcport': srcport, 'dstport': dstport, 'type': type_list})
edges_l = pd.DataFrame.from_dict(
    {'from': from_node, 'to': to_node, 'srcport': srcport, 'dstport': dstport, 'mode': mode_list})
nodes_p = set()
nodes_l = set()

# edgeとnodeのリストを作成(物理図と論理図それぞれ用意)
cy_edges_p = []
cy_nodes_p = []
cy_edges_l = []
cy_nodes_l = []

# 物理図用のノード・エッジデータ作成
for index, row in edges_p.iterrows():
    # source node, target nodeのid(ループ用、物理図用、論理図用)
    source, target, source_label, target_label = row['from'], row['to'], row['srcport'], row['dstport']
    source_p, target_p, source_label_p, target_label_p, src_type = row['from'], row['to'], row['srcport'], row[
        'dstport'], row['type']
    if source not in nodes_p:
        nodes_p.add(source)
        # classesはdata{}の外に書く
        if source in [core_primary, core_secondary]:
            cy_nodes_p.append({'data': {'id': source_p, 'label': source_p, 'model': 'L3switch'}, 'classes': 'L3switch'})
        else:
            cy_nodes_p.append({'data': {'id': source_p, 'label': source_p, 'model': 'L2switch'}, 'classes': 'L2switch'})
    if target not in nodes_p:
        nodes_p.add(target)
        if target in [core_primary, core_secondary]:
            cy_nodes_p.append({'data': {'id': target_p, 'label': target_p, 'model': 'L3switch'}, 'classes': 'L3switch'})
        else:
            if source in [core_primary, core_secondary]:  # コアと直接つながっていたらディストリ
                cy_nodes_p.append(
                    {'data': {'id': target_p, 'label': target_p, 'model': 'L2switch'}, 'classes': 'L2_dist'})
            else:  # そうでなければエッジ
                cy_nodes_p.append(
                    {'data': {'id': target_p, 'label': target_p, 'model': 'L2switch'}, 'classes': 'L2_edge'})
    cy_edges_p.append({
        # srcportとdstportは独自キー
        'data': {
            'source': source_p,
            'target': target_p,
            'srcport': source_label_p,
            'dstport': target_label_p
        },
        'classes': src_type
    })

# 論理図用のノード・エッジデータ作成
for index, row in edges_l.iterrows():
    # source node, target nodeのid(ループ用、物理図用、論理図用)
    source, target, source_label, target_label = row['from'], row['to'], row['srcport'], row['dstport']
    source_l, target_l, source_label_l, target_label_l, src_mode = row['from'], row['to'], row['srcport'], row[
        'dstport'], row['mode']
    if source not in nodes_l:
        nodes_l.add(source)
        # classesはdata{}の外に書く
        if source in [core_primary, core_secondary]:
            cy_nodes_l.append(
                {'data': {'id': source_l, 'label': source_l, 'model': 'L3switch'}, 'classes': 'L3switch'})
        else:
            cy_nodes_l.append(
                {'data': {'id': source_l, 'label': source_l, 'model': 'L2switch'}, 'classes': 'L2switch'})
    if target not in nodes_l:
        nodes_l.add(target)
        if target in [core_primary, core_secondary]:
            cy_nodes_l.append(
                {'data': {'id': target_l, 'label': target_l, 'model': 'L3switch'}, 'classes': 'L3switch'})
        else:
            if source in [core_primary, core_secondary]:  # コアと直接つながっていたらディストリ
                cy_nodes_l.append(
                    {'data': {'id': target_l, 'label': target_l, 'model': 'L2switch'}, 'classes': 'L2_dist'})
            else:  # そうでなければエッジ
                cy_nodes_l.append(
                    {'data': {'id': target_l, 'label': target_l, 'model': 'L2switch'}, 'classes': 'L2_edge'})
    cy_edges_l.append({
        # srcportとdstportは独自キー
        'data': {
            'source': source_l,
            'target': target_l,
            'srcport': source_label_l,
            'dstport': target_label_l
        },
        'classes': src_mode
    })

# スタイル指定のためのjson読み込み
json_open_default = open('assets/default.json')
json_open_universe = open('assets/universe.json')
json_open_flower = open('assets/flower.json')
json_load_default = json.load(json_open_default)
json_load_universe = json.load(json_open_universe)
json_load_flower = json.load(json_open_flower)

# 変数を使うスタイル指定
common_style = [
    {
        # selectorの中に条件を定義すると特定のnode,edgeにスタイルを適用できる
        # Group selectors
        'selector': 'node',  # すべてのnodeに対して適用
        'style': {
            'content': 'data(id)',
        }
    },
    {
        'selector': 'edge',  # すべてのedgeに対して
        'style': {
            "source-label": "data(srcport)",
            "target-label": "data(dstport)"
        }
    }]

# 各デザインのスタイル
default_stylesheet = common_style + json_load_default
universe_stylesheet = common_style + json_load_universe
flower_stylesheet = common_style + json_load_flower

graph_layout = {
    'name': 'breadthfirst',
    'roots': '#' + core_primary + ',' '#' + core_secondary
}

# ページ左側のエリアのレイアウト
# デザインのドロップダウンコンポーネント
theme_dropdown = dcc.Dropdown(
    id='theme_dropdown',
    options=[
        {'label': '標準', 'value': 'default'},
        {'label': '宇宙', 'value': 'universe'},
        {'label': '花', 'value': 'flower'}
    ],
    # value='default',  # 初期値の設定
    placeholder='デザインを選択',
    clearable=False,
    className='theme'
)

# 物理図
graph_p = cyt.Cytoscape(
    id='graph_p',  # Cytoscape自体にもid,layout,styleが必要
    elements=cy_edges_p + cy_nodes_p,
    style={
        'height': '95vh',
        'width': '100%'
    },
    stylesheet=default_stylesheet,
    layout=graph_layout
)

# 論理図
graph_l = cyt.Cytoscape(
    id='graph_l',  # Cytoscape自体にもid,layout,styleが必要
    elements=cy_edges_l + cy_nodes_l,
    style={
        'height': '95vh',
        'width': '100%'
    },
    stylesheet=default_stylesheet,
    layout=graph_layout
)

# 物理図ページのDivのchildren属性に渡すレイアウト(左側)
left_p = html.Div(
    [theme_dropdown,
     dcc.Link('物理情報', href='/apps/physical', className='app_link'),
     dcc.Link('論理情報', href='/apps/logical', className='app_link'),
     graph_p],
    className='left',
    id='left_p'
)
# 論理図ページのDivのchildren属性に渡すレイアウト(左側)
left_l = html.Div(
    [theme_dropdown,
     dcc.Link('物理情報', href='/apps/physical', className='app_link'),
     dcc.Link('論理情報', href='/apps/logical', className='app_link'),
     graph_l],
    className='left',
    id='left_l'
)

# ページ右側のエリアのレイアウト
# コマンドのドロップダウンコンポーネント
command_dropdown_p = dcc.Dropdown(
    id='command_dropdown_p',
    options=[
        {'label': 'ポートステータス(show interfaces status)', 'value': 'port'},
        {'label': 'マックアドレステーブル(show mac-address-table)', 'value': 'mac'},
        {'label': 'ルーティングテーブル(show ip route)', 'value': 'route'},
        {'label': 'IPインターフェース情報( show ip interface brief)', 'value': 'ip_int'},
        {'label': 'コンフィグ(show running-config)', 'value': 'run'},
    ],
    placeholder='閲覧したい情報を選択',
    clearable=False,
    className='command',
    style={
        'visibility': 'hidden'
    }
)
command_dropdown_l = dcc.Dropdown(
    id='command_dropdown_l',
    options=[
        {'label': 'ポートステータス(show interfaces status)', 'value': 'port'},
        {'label': 'マックアドレステーブル(show mac-address-table)', 'value': 'mac'},
        {'label': 'ルーティングテーブル(show ip route)', 'value': 'route'},
        {'label': 'IPインターフェース情報( show ip interface brief)', 'value': 'ip_int'},
        {'label': 'コンフィグ(show running-config)', 'value': 'run'},
    ],
    placeholder='閲覧したい情報を選択',
    clearable=False,
    className='command',
    style={
        'visibility': 'hidden'
    }
)

# 物理図ページのDivのchildren属性に渡すレイアウト(右側)
right_p = html.Div(
    children=[html.H2(id='table_title_p'),
              command_dropdown_p,
              html.Div(id='table_p')],
    className='right',
    id='right_p'
)
# 論理図ページのDivのchildren属性に渡すレイアウト(右側)
right_l = html.Div(
    children=[html.H2(id='table_title_l'),
              command_dropdown_l,
              html.Div(id='table_l')],
    className='right',
    id='right_l'
)

# ページ全体のレイアウト作成
# 物理図ページのレイアウト
layout_p = html.Div(
    children=[
        html.H1('Penguin Viewer'),
        html.Div([left_p, right_p])],
    id='html_p',
    style={'backgroundColor': '#D7EEFF',
           'display': 'block',
           'overflow-x': 'scroll',
           'white-space': 'nowrap'})
# 論理図ページのレイアウト
layout_l = html.Div(
    children=[
        html.H1('Penguin Viewer'),
        html.Div([left_l, right_l])],
    id='html_l',
    style={'backgroundColor': '#D7EEFF',
           'display': 'block',
           'overflow-x': 'scroll',
           'white-space': 'nowrap'})
