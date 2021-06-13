# JSONファイルを読み込んでネットワーク図を描画するプログラム。
import datetime as dt
import json
import os
import pathlib

import dash
import dash_cytoscape as cyt
import dash_html_components as html


output_folder = './output/'

# デフォルトでは最新のファイルを開くようにしてユーザの選択により過去ファイルも開くようにしたい。
json_files = list(pathlib.Path(output_folder).glob("*"))
file_updates = {file_path: os.stat(file_path).st_mtime for file_path in json_files}
latest_json_file = max(file_updates, key=file_updates.get)

latest_graph = open(latest_json_file, 'r')
graph_data = json.load(latest_graph)  # JSONの読み込み

graph_year = os.path.basename(latest_json_file)[0:4]
graph_month = os.path.basename(latest_json_file)[4:6]
graph_day = os.path.basename(latest_json_file)[6:8]
graph_hour = os.path.basename(latest_json_file)[9:11]
graph_minute = os.path.basename(latest_json_file)[11:13]

print(latest_json_file)

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

app = dash.Dash(__name__, title='Penguin Viewer')
app.config.suppress_callback_exceptions = True
server = app.server

app.layout = html.Div(
    children=[
        html.H1('Penguin Viewer'),
        html.H2(graph_year + '/' + graph_month + '/' + graph_day + ' ' + graph_hour + ':' + graph_minute + 'のネットワーク図'),
        html.Div(graph)],
    id='html',
    style={'backgroundColor': '#D7EEFF',
           'display': 'block',
           'overflow-x': 'scroll',
           'white-space': 'nowrap'})

if __name__ == '__main__':
    app.run_server(debug=False)
