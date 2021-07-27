from dash.dependencies import Input, Output, State
from app import app

from layouts import default_stylesheet, universe_stylesheet, flower_stylesheet, command_dropdown

import dash_table


# ドロップダウンでスタイルを変更する。マウスをかざしたノードの色を変更する。
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
@app.callback(
    Output('hostname', 'children'),  # valueではなくchildren
    Output('ipaddr', 'children'),
    Output('macaddr', 'children'),
    Output('model', 'children'),
    Output('vtp', 'children'),
    Output('left', 'style'),
    Output('right', 'style'),
    Input('graph', 'tapNodeData'),
    prevent_initial_call=True
)
def show_node_info(clicked_node_dict):
    # クリックされたノードのidを取得
    clicked_node_name = clicked_node_dict['id']
    clicked_node_ip = 'IPアドレス：' + clicked_node_dict['ipaddr']
    clicked_node_mac = 'MACアドレス：' + clicked_node_dict['macaddr']
    clicked_node_model = '機種：' + clicked_node_dict['model']
    clicked_node_vtp = 'VTPドメイン：' + clicked_node_dict['vtp_domain'] + ', VTPモード：' + clicked_node_dict['vtp_mode']

    # 幅の変更とテーブルの表示
    left_style = {'width': '55%'}
    right_style = {'width': '45%',
                   'visibility': 'visible'}
    return clicked_node_name, clicked_node_ip, clicked_node_mac, clicked_node_model, clicked_node_vtp, left_style, right_style


# 各種出力ボタンがクリックされたらコマンドドロップダウンを表示する。
@app.callback(
    Output('command_area', 'children'),
    Input('show_button', 'n_clicks'),
    prevent_initial_call=True
)
def show_command_dropdown(n_clicks):
    if n_clicks != 0:
        return command_dropdown


# コマンドドロップダウンで選択されたコマンドの出力を表示する。
@app.callback(
    Output('table_area', 'children'),
    Input('graph', 'tapNodeData'),
    Input('command_dropdown', 'value'),
    prevent_initial_call=True
)
def show_table(clicked_node_dict, command):
    if command is None:
        pass
    else:
        # コマンド出力表の生成
        if command == 'interface_status':
            table_columns = [
                {'name': 'Port', 'id': 'Port'},
                {'name': 'Description', 'id': 'Description'},
                {'name': 'Status', 'id': 'Status'},
                {'name': 'Vlan', 'id': 'Vlan'},
                {'name': 'Duplex', 'id': 'Duplex'},
                {'name': 'Speed', 'id': 'Speed'},
                {'name': 'Type', 'id': 'Type'}
            ]
        elif command == 'int_brief':
            table_columns = [
                {'name': 'Intf', 'id': 'Intf'},
                {'name': 'Ipaddr', 'id': 'Ipaddr'},
                {'name': 'Status', 'id': 'Status'},
                {'name': 'Proto', 'id': 'Proto'},
            ]
        elif command == 'ip_route':
            table_columns = [
                {'name': 'Protocol', 'id': 'Protocol'},
                {'name': 'Type', 'id': 'Type'},
                {'name': 'Network', 'id': 'Network'},
                {'name': 'Mask', 'id': 'Mask'},
                {'name': 'Distance', 'id': 'Distance'},
                {'name': 'Metric', 'id': 'Metric'},
                {'name': 'Nexthop_ip', 'id': 'Nexthop_ip'},
                {'name': 'Nexthop_if', 'id': 'Nexthop_if'},
                {'name': 'Uptime', 'id': 'Uptime'},
            ]
        elif command == 'mac_table':
            table_columns = [
                {'name': 'Dst_addr', 'id': 'Dst_addr'},
                {'name': 'Type', 'id': 'Type'},
                {'name': 'Vlan', 'id': 'Vlan'},
                {'name': 'Dst_port', 'id': 'Dst_port'},
            ]
        elif command == 'ip_arp':
            table_columns = [
                {'name': 'Protocol', 'id': 'Protocol'},
                {'name': 'Address', 'id': 'Address'},
                {'name': 'Age', 'id': 'Age'},
                {'name': 'Mac', 'id': 'Mac'},
                {'name': 'Type', 'id': 'Type'},
                {'name': 'Interface', 'id': 'Interface'},
            ]
        else:
            table_columns = None

        table_data = dash_table.DataTable(
            # columnsにデータを渡す
            columns=table_columns,
            # dataにデータを渡す
            # dataのキーとcolumnsのidが一致するように！
            data=clicked_node_dict[command],  # jsonから読み取るポートリスト
            # テーブルを画面いっぱいに広げるかどうか
            fill_width=False,  # 広げない
            style_cell={'fontSize': 18, 'textAlign': 'center'},
            style_header={'background-color': '#D7EEFF'}  # テーブルヘッダのスタイル
        )
        return table_data


'''
# 現在のインターフェースステータスを取得して表示する。
@app.callback(
    Output('table_area', 'children'),
    Input('graph', 'tapNodeData'),
    Input('status_button', 'n_clicks'),
    prevent_inital_call=True
)
def show_status_now(clicked_node_dict, n_clicks):
    if n_clicks != 0:
        clicked_node_info = {'device_type': 'autodetect',
                           'host': clicked_node_dict['ipaddr'],
                           'username': ,
                           'password': }
'''


# グラフのレイアウトを変更する
@app.callback(
    Output('graph', 'layout'),
    Input('apply_button', 'n_clicks'),  # Input fires callbacks. State doesn't.
    State('core_hostname', 'value')
)
def change_layout(n_clicks, core):
    if n_clicks != 0 and core:
        new_layout = {
            'name': 'breadthfirst',
            'roots': '#' + core
        }
        return new_layout
    else:
        pass
