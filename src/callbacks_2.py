from dash.dependencies import Input, Output
from app import app

from layouts import default_stylesheet, universe_stylesheet, flower_stylesheet

import dash_table


# ドロップダウンでスタイルを変更し、マウスをかざしたノードの機種名を表示する
@app.callback(
    Output('graph', 'stylesheet'),  # グラフ部分のスタイル
    Output('html', 'style'),  # ページ全体のスタイル
    Input('theme_dropdown', 'value'),  # ドロップダウンで選択されたデザインの種類
    Input('graph', 'mouseoverNodeData'),  # マウスをかざしたノードのデータ辞書を受け取る
)
def update_graph(theme, node_data_dict):  # Inputの値が引数になる。
    # 選択したテーマ用のスタイル
    if theme == 'universe' == 'universe':
        selected_stylesheet = universe_stylesheet
        html_style = {'backgroundColor': 'black'}  # ページ全体の背景
    elif theme == 'flower':
        selected_stylesheet = flower_stylesheet
        html_style = {'backgroundColor': '#f5ecf4'}  # ページ全体の背景
    else:
        selected_stylesheet = default_stylesheet
        html_style = {'backgroundColor': '#D7EEFF'}  # ページ全体の背景

    if node_data_dict:  # ノードにマウスがかざされたとき
        # ノードの枠線およびラベル表示変更(機種名表示)
        style_with_label = [{'selector': '#' + node_data_dict['id'],
                             'style': {
                                 'label': (node_data_dict['model']),
                                 'border-width': 5,
                                 'border-style': 'double',
                                 'border-color': '#8b008b',
                                 'border-opacity': 0.9}}]

        updated_stylesheet = selected_stylesheet + style_with_label

    else:
        updated_stylesheet = selected_stylesheet
    # データが取れてるか
    # print(node_data_dict['model'])
    print(updated_stylesheet)
    return updated_stylesheet, html_style


# ノードがクリックされたらグラフエリアを縮小してノード名を表示する。
# (ノードがクリックされていないと返り値が得られずエラーを吐く模様。)
@app.callback(
    Output('table_title', 'value'),
    Output('left', 'style'),
    Output('right', 'style'),
    Input('graph', 'tapNodeData'),
)
def show_table(clicked_node_dict):
    if clicked_node_dict:
        # クリックされたノードのidを取得
        clicked_node_name = clicked_node_dict['id']
        # 幅の変更とテーブルの表示
        left_style = {'width': '70%'}
        right_style = {'width': '30%',
                       'visibility': 'visible'}
        return clicked_node_name, left_style, right_style
    else:
        pass


# クリックされたノードの出力表を表示する。
@app.callback(
    Output('table', 'children'),
    Input('graph', 'tapNodeData'),
    Input('command_dropdown', 'value')
)
def show_table(clicked_node_dict, command):
    # コマンド出力表の生成
    if command == 'port':
        table_columns = [
            {'name': 'Port', 'id': 'Port'},
            {'name': 'Description', 'id': 'Description'},
            {'name': 'Status', 'id': 'Status'},
            {'name': 'Vlan', 'id': 'Vlan'},
            {'name': 'Duplex', 'id': 'Duplex'},
            {'name': 'Speed', 'id': 'Speed'},
            {'name': 'Type', 'id': 'Type'}
        ]
    elif command == 'ip_int':
        table_columns = [
            {'name': 'Intf', 'id': 'Intf'},
            {'name': 'Ipaddr', 'id': 'Ipaddr'},
            {'name': 'Status', 'id': 'Status'},
            {'name': 'Proto', 'id': 'Proto'},
        ]
    elif command == 'vtp':
        table_columns = [
            {'name': 'Port', 'id': 'Port'},
            {'name': 'Description', 'id': 'Description'},
            {'name': 'Status', 'id': 'Status'},
            {'name': 'Vlan', 'id': 'Vlan'},
            {'name': 'Duplex', 'id': 'Duplex'},
            {'name': 'Speed', 'id': 'Speed'},
            {'name': 'Type', 'id': 'Type'}
        ]
    elif command == 'route':
        table_columns = [
            {'name': 'Port', 'id': 'Port'},
            {'name': 'Description', 'id': 'Description'},
            {'name': 'Status', 'id': 'Status'},
            {'name': 'Vlan', 'id': 'Vlan'},
            {'name': 'Duplex', 'id': 'Duplex'},
            {'name': 'Speed', 'id': 'Speed'},
            {'name': 'Type', 'id': 'Type'}
        ]
    elif command == 'mac':
        table_columns = [
            {'name': 'Port', 'id': 'Port'},
            {'name': 'Description', 'id': 'Description'},
            {'name': 'Status', 'id': 'Status'},
            {'name': 'Vlan', 'id': 'Vlan'},
            {'name': 'Duplex', 'id': 'Duplex'},
            {'name': 'Speed', 'id': 'Speed'},
            {'name': 'Type', 'id': 'Type'}
        ]
    elif command == 'arp':
        table_columns = [
            {'name': 'Port', 'id': 'Port'},
            {'name': 'Description', 'id': 'Description'},
            {'name': 'Status', 'id': 'Status'},
            {'name': 'Vlan', 'id': 'Vlan'},
            {'name': 'Duplex', 'id': 'Duplex'},
            {'name': 'Speed', 'id': 'Speed'},
            {'name': 'Type', 'id': 'Type'}
        ]
    else:
        table_columns = [
            {'name': 'Port', 'id': 'Port'}]

    table_data = dash_table.DataTable(
        # columnsにデータを渡す
        columns=table_columns,
        # dataにデータを渡す
        # dataのキーとcolumnsのidが一致するように！
        data=clicked_node_dict['interface_status'],  # jsonから読み取るポートリスト
        # テーブルを画面いっぱいに広げるかどうか
        fill_width=False,  # 広げない
        style_cell={'fontSize': 18, 'textAlign': 'center'},
        style_header={'background-color': '#D7EEFF'}  # テーブルヘッダのスタイル
    )
    return table_data
