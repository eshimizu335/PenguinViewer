# JSONファイルを読み込んでネットワーク図を描画するプログラム。
import json
import os
import pathlib

import dash
import dash_cytoscape as cyt
import dash_html_components as html

from app import app

output_folder = '../output/'
assets_folder = './assets/'

# デフォルトでは最新のファイルを開くようにしてユーザの選択により過去ファイルも開くようにしたい。
json_files = list(pathlib.Path(output_folder).glob("*"))
file_updates = {file_path: os.stat(file_path).st_mtime for file_path in json_files}
latest_json_file = max(file_updates, key=file_updates.get)

latest_graph = open(latest_json_file, 'r')
graph_data = json.load(latest_graph)  # JSONの読み込み

access_time = os.path.basename(latest_json_file)    # ファイル名からスイッチへのアクセス時刻を取得

# スタイル指定のためのjson読み込み
json_open_default = open(assets_folder + 'default.json')
json_open_universe = open(assets_folder + 'universe.json')
json_open_flower = open(assets_folder + 'flower.json')
json_load_default = json.load(json_open_default)
json_load_universe = json.load(json_open_universe)
json_load_flower = json.load(json_open_flower)

graph_layout = {
    'name': 'circle'
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


app.layout = html.Div(
    children=[
        html.H1('Penguin Viewer'),
        html.H2(access_time[0:4] + '/' + access_time[4:6] + '/' + access_time[6:8] + ' ' + access_time[9:11] + ':' + access_time[11:13] + 'のネットワーク図'),
        html.Div(graph)],
    id='html',
    style={'backgroundColor': '#D7EEFF',
           'display': 'block',
           'overflow-x': 'scroll',
           'white-space': 'nowrap'})

if __name__ == '__main__':
    app.run_server(debug=False)
