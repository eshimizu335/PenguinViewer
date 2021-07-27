# JSONファイルを読み込んでネットワーク図を描画するプログラム。
import json
import os
import pathlib

import dash
import dash_core_components as dcc
import dash_cytoscape as cyt
import dash_html_components as html
import dash_table

from app import app

output_folder = '../output/'
assets_folder = './assets/'

# デフォルトでは最新のファイルを開くようにしてユーザの選択により過去ファイルも開くようにしたい。
json_files = list(pathlib.Path(output_folder).glob("*"))
file_updates = {file_path: os.stat(file_path).st_mtime for file_path in json_files}
latest_json_file = max(file_updates, key=file_updates.get)

latest_graph = open(latest_json_file, 'r')
graph_data = json.load(latest_graph)  # JSONの読み込み

access_time = os.path.basename(latest_json_file)  # ファイル名からスイッチへのアクセス時刻を取得

# スタイル指定のためのjson読み込み
json_open_default = open(assets_folder + 'default.json')
json_open_universe = open(assets_folder + 'universe.json')
json_open_flower = open(assets_folder + 'flower.json')
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

# ページ左側のコンテンツ
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

core_hostname = dcc.Input(
    id='core_hostname',
    type='text',
    placeholder='コアスイッチのホスト名を入力'
)

apply_button = html.Button('適用', id='apply_button')

graph_layout = {
    'name': 'random',
    # 'roots': '#' + core
}
graph = cyt.Cytoscape(
    id='graph',  # Cytoscape自体にもid,layout,styleが必要
    elements=graph_data,
    style={
        'height': '95vh',
        'width': '100%'
    },
    layout=graph_layout
)

# ページ左側のレイアウト
left = html.Div(
    [theme_dropdown,
     html.Div([core_hostname, apply_button]),
     html.Div(id='vlan'),
     graph],
    className='left',
    id='left',
    style={'width': '100%'}
)

# ページ右側のコンテンツ

show_button = html.Button('各種出力', id='show_button')
status_button = html.Button('現在のポートステータス', id='status_button')
ping_button = html.Button('ping', id='ping_button')

command_dropdown = dcc.Dropdown(
    id='command_dropdown',
    options=[
        {'label': '隣接機器情報(show cdp neighbors)', 'value': 'cdp'},
        {'label': 'ポートステータス(show interfaces status)', 'value': 'interface_status'},
        {'label': 'IPインターフェース情報( show ip interface brief)', 'value': 'int_brief'},
        {'label': 'ルーティングテーブル(show ip route)', 'value': 'ip_route'},
        {'label': 'マックアドレステーブル(show mac-address-table)', 'value': 'mac_table'},
        {'label': 'arp情報(show ip arp)', 'value': 'ip_arp'},

    ],
    placeholder='閲覧したい情報を選択',
    clearable=False,
    className='command'
)
# ページ右側のレイアウト
right = html.Div(
    children=[html.H2(id='hostname'),
              html.H3(id='ipaddr'),
              html.H3(id='macaddr'),
              html.H3(id='model'),
              html.H3(id='vtp'),
              show_button,
              status_button,
              ping_button,
              html.Div(id='status_area'),
              html.Div(id='command_area'),
              html.Div(id='table_area')],  # テーブル表示エリアは空のDivにしてidをつけておく
    className='right',
    id='right',
)

layout_html = html.Div(
    children=[html.H1('Penguin Viewer'),
              html.H2(access_time[0:4] + '/' + access_time[4:6] + '/' + access_time[6:8] + ' ' + access_time[
                                                                                                 9:11] + ':' + access_time[
                                                                                                               11:13] + 'のネットワーク図'),
              html.Div([left, right])],
    id='html',
    style={'backgroundColor': '#D7EEFF',
           'display': 'block',
           'overflow-x': 'scroll',
           'white-space': 'nowrap'})
