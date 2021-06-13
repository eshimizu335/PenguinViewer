import dash
from dash.dependencies import Input, Output
from app import app

from layouts import default_stylesheet, universe_stylesheet, flower_stylesheet
from read import check_model
import table


# 物理図上でマウスをかざしたノードのデータ辞書を表示し、ドロップダウンでスタイルを変更するコールバック関数
@app.callback(
    Output('graph_p', 'stylesheet'),  # 出力先IDとして物理図のID'graph_p'を指定。属性stylesheetに出力する
    Output('html_p', 'style'),  # 出力先IDとして物理図ページのID'hmtl_p'を指定。属性styleに出力する
    Output('left_p', 'style'),
    Output('right_p', 'style'),
    [Input('graph_p', 'mouseoverNodeData')],  # マウスをかざしたノードのデータ辞書を受け取る
    [Input('graph_p', 'tapEdgeData')],  # クリックしたエッジのデータ辞書を受け取る
    [Input('graph_p', 'tapNodeData')],  # クリックしたノードのデータ辞書を受け取る
    [Input('theme_dropdown', 'value')],  # ドロップダウンコンポーネントのID'theme_dropdown'を指定。属性valueを渡す
)
def update_graph_p(node_data_dict, edge_data_dict, clicked_node_dict, theme):  # グラフのテーマを変える
    # 選択したテーマ用のスタイル
    if theme == 'universe':
        selected_stylesheet = universe_stylesheet
        wstyle = {'backgroundColor': 'black'}  # ページ全体の背景
    elif theme == 'flower':
        selected_stylesheet = flower_stylesheet
        wstyle = {'backgroundColor': '#f5ecf4'}
    else:
        selected_stylesheet = default_stylesheet
        wstyle = {'backgroundColor': '#D7EEFF'}

    if node_data_dict:  # ノードにマウスがかざされたとき
        if node_data_dict['model'] == 'L3switch':  # かざしたノードがL3だったら
            # ノードの枠線およびラベル表示変更(機種名表示)
            style_with_label = {'selector': '#' + node_data_dict['id'],
                                'style': {
                                    'label': check_model(node_data_dict['id']),
                                    'border-width': 5,
                                    'border-style': 'double',
                                    'border-color': '#8b008b',
                                    'border-opacity': 0.9}}
        else:  # かざしたノードがL2だったら
            style_with_label = {'selector': '#' + node_data_dict['id'],
                                'style': {
                                    'label': check_model(node_data_dict['id']),
                                    'border-width': 5,
                                    'border-style': 'double',
                                    'border-color': '#da70d6',
                                    'border-opacity': 0.9}}
        if clicked_node_dict:  # ノードがクリックされたら
            left_style = {'width': '70%', 'overflow': 'auto'}
            right_style = {'width': '30%', 'overflow': 'auto'}
            if clicked_node_dict['model'] == 'L3switch':  # クリックされたのがL3だったら
                # ノードの色変更
                style_node_clicked = {'selector': '#' + clicked_node_dict['id'],
                                      'style': {
                                          'backgroundColor': '#8b008b'}}
            else:  # クリックされたのがL2だったら
                # ノードの色変更
                style_node_clicked = {'selector': '#' + clicked_node_dict['id'],
                                      'style': {
                                          'backgroundColor': '#da70d6'}}
            if edge_data_dict:  # edgeがクリックされたら
                source_info_list = table.format_data_interface(edge_data_dict['source'])  # sourceのインターフェース情報を取得
                for source_info in source_info_list:
                    # srcportと同じインターフェースだったら
                    # sh interfaces statusの出力からケーブルの種類を判断
                    if source_info['Port'] == edge_data_dict['srcport']:
                        if source_info['Type'] == '10/100BaseTX':
                            cable = 'UTP-1GB'
                        elif source_info['Type'] == '10GBASE-T':
                            cable = 'UTP-10GB'
                        elif source_info['Type'] == '1000BASE-SX':
                            cable = '光マルチ-1GB'
                        elif source_info['Type'] == '1000BASE-LX':
                            cable = '光シングル-1GB'
                        elif source_info['Type'] == '10GBASE-SR':
                            cable = '光マルチ-10GB'
                        elif source_info['Type'] == '10GBASE-LR':
                            cable = '光シングル-10GB'
                        else:
                            cable = 'ケーブル不明'
                        # エッジの太さ変更とラベル表示(ケーブル情報)
                        style_edge_label = {'selector': '#' + edge_data_dict['id'],
                                            'style': {
                                                'width': 10,
                                                'label': cable,
                                                'text-background-color': 'white',
                                                'text-background-opacity': 0.9,
                                                'text-background-shape': 'rectangle',
                                                'text-background-padding': '3px',
                                                'font-size': 20}}
                        updated_stylesheet = selected_stylesheet + [style_with_label] + [style_node_clicked] + [
                            style_edge_label]
                        return updated_stylesheet, wstyle, left_style, right_style
                    else:
                        pass
            else:  # edgeがクリックされなければ
                updated_stylesheet = selected_stylesheet + [style_with_label] + [style_node_clicked]
                return updated_stylesheet, wstyle, left_style, right_style
        else:  # ノードがクリックされてなかったら
            left_style = {'width': '100%'}
            right_style = {'width': '0%'}
            if edge_data_dict:  # edgeがクリックされたら
                source_info_list = table.format_data_interface(edge_data_dict['source'])  # sourceのインターフェース情報を取得
                for source_info in source_info_list:
                    # srcportと同じインターフェースだったら(cdpの出力はインターフェース名にスペース入ってるのでreplaceで消す)
                    # sh interfaces statusの出力からケーブルの種類を判断
                    if source_info['Port'] == edge_data_dict['srcport'].replace(' ', ''):
                        if source_info['Type'] == '10/100BaseTX':
                            cable = 'UTP-1GB'
                        elif source_info['Type'] == '10GBASE-T':
                            cable = 'UTP-10GB'
                        elif source_info['Type'] == '1000BASE-SX':
                            cable = '光マルチ-1GB'
                        elif source_info['Type'] == '1000BASE-LX':
                            cable = '光シングル-1GB'
                        elif source_info['Type'] == '10GBASE-SR':
                            cable = '光マルチ-10GB'
                        elif source_info['Type'] == '10GBASE-LR':
                            cable = '光シングル-10GB'
                        else:
                            cable = 'ケーブル不明'
                        # エッジの太さ変更とラベル表示(ケーブル情報)
                        style_edge_label = {'selector': '#' + edge_data_dict['id'],
                                            'style': {
                                                'width': 10,
                                                'label': cable,
                                                'text-background-color': 'white',
                                                'text-background-opacity': 0.9,
                                                'text-background-shape': 'rectangle',
                                                'text-background-padding': '3px',
                                                'font-size': 20}}
                        updated_stylesheet = selected_stylesheet + [style_with_label] + [style_edge_label]
                        return updated_stylesheet, wstyle, left_style, right_style
            else:  # edgeがクリックされなければ
                updated_stylesheet = selected_stylesheet + [style_with_label]
                return updated_stylesheet, wstyle, left_style, right_style
    else:  # ノードにマウスがかざされていないとき
        left_style = {'width': '100%'}
        right_style = {'width': '0%'}
        if edge_data_dict:  # edgeがクリックされたら
            source_info_list = table.format_data_interface(edge_data_dict['source'])  # sourceのインターフェース情報を取得
            for source_info in source_info_list:
                # srcportと同じインターフェースだったら(cdpの出力はインターフェース名にスペース入ってるのでreplaceで消す)
                # sh interfaces statusの出力からケーブルの種類を判断
                if source_info['Port'] == edge_data_dict['srcport'].replace(' ', ''):
                    if source_info['Type'] == '10/100BaseTX':
                        cable = 'UTP-1GB'
                    elif source_info['Type'] == '10GBASE-T':
                        cable = 'UTP-10GB'
                    elif source_info['Type'] == '1000BASE-SX':
                        cable = '光マルチ-1GB'
                    elif source_info['Type'] == '1000BASE-LX':
                        cable = '光シングル-1GB'
                    elif source_info['Type'] == '10GBASE-SR':
                        cable = '光マルチ-10GB'
                    elif source_info['Type'] == '10GBASE-LR':
                        cable = '光シングル-10GB'
                    else:
                        cable = 'ケーブル不明'
                    # エッジの太さ変更とラベル表示(ケーブル情報)
                    style_edge_label = {'selector': '#' + edge_data_dict['id'],
                                        'style': {
                                            'width': 10,
                                            'label': cable,
                                            'text-background-color': 'white',
                                            'text-background-opacity': 0.9,
                                            'text-background-shape': 'rectangle',
                                            'text-background-padding': '3px',
                                            'font-size': 20}}
                    edge_updated_stylesheet = selected_stylesheet + [style_edge_label]
                    return edge_updated_stylesheet, wstyle, left_style, right_style
                else:
                    pass
        else:  # 何も起きていなければ

            return selected_stylesheet, wstyle, left_style, right_style


# 論理図上でマウスをかざしたノードのデータ辞書を表示するコールバック関数と、ドロップダウンでスタイルを変更するコールバック関数
@app.callback(
    Output('graph_l', 'stylesheet'),
    Output('html_l', 'style'),
    Output('left_l', 'style'),
    Output('right_l', 'style'),
    [Input('graph_l', 'mouseoverNodeData')],  # マウスをかざしたノードのデータ辞書を受け取る
    [Input('graph_l', 'tapEdgeData')],  # クリックしたエッジのデータ辞書を受け取る
    [Input('graph_l', 'tapNodeData')],  # クリックしたノードのデータ辞書を受け取る
    [Input('theme_dropdown', 'value')],
)
def update_graph_l(node_data_dict, edge_data_dict, clicked_node_dict, theme):  # グラフのテーマと画面全体のスタイルを変える
    # 選択したテーマ用のスタイル
    if theme == 'universe' == 'universe':
        selected_stylesheet = universe_stylesheet
        wstyle = {'backgroundColor': 'black'}
    elif theme == 'flower':
        selected_stylesheet = flower_stylesheet
        wstyle = {'backgroundColor': '#f5ecf4'}
    else:
        selected_stylesheet = default_stylesheet
        wstyle = {'backgroundColor': '#D7EEFF'}
    if node_data_dict:  # ノードにマウスがかざされたとき
        if node_data_dict['model'] == 'L3switch':  # かざしたノードがL3だったら
            # ノードの枠線およびラベル表示変更(機種名表示)
            style_with_label = {'selector': '#' + node_data_dict['id'],
                                'style': {
                                    'label': check_model(node_data_dict['id']),
                                    'border-width': 5,
                                    'border-style': 'double',
                                    'border-color': '#8b008b',
                                    'border-opacity': 0.9}}
        else:  # かざしたノードがL2だったら
            style_with_label = {'selector': '#' + node_data_dict['id'],
                                'style': {
                                    'label': check_model(node_data_dict['id']),
                                    'border-width': 5,
                                    'border-style': 'double',
                                    'border-color': '#da70d6',
                                    'border-opacity': 0.9}}
        if clicked_node_dict:  # ノードがクリックされたら
            left_style = {'width': '70%', 'overflow': 'auto'}
            right_style = {'width': '30%', 'overflow': 'auto'}
            if clicked_node_dict['model'] == 'L3switch':  # クリックされたのがL3だったら
                # ノードの色変更
                style_node_clicked = {'selector': '#' + clicked_node_dict['id'],
                                      'style': {
                                          'backgroundColor': '#8b008b'}}
            else:  # クリックされたのがL2だったら
                # ノードの色変更
                style_node_clicked = {'selector': '#' + clicked_node_dict['id'],
                                      'style': {
                                          'backgroundColor': '#da70d6'}}
            if edge_data_dict:  # edgeがクリックされたら
                source_info_list = table.format_data_interface(
                    edge_data_dict['source'])  # sourceのインターフェース情報を取得
                for source_info in source_info_list:
                    # srcportと同じインターフェースだったら(cdpの出力はインターフェース名にスペース入ってるのでreplaceで消す)
                    if source_info['Port'] == edge_data_dict['srcport'].replace(' ', ''):
                        # エッジの太さ変更とラベル表示(Vlan情報)
                        style_edge_label = {'selector': '#' + edge_data_dict['id'],
                                            'style': {
                                                'width': 10,
                                                'label': 'Vlan' + source_info['Vlan'],
                                                'text-background-color': 'white',
                                                'text-background-opacity': 0.9,
                                                'text-background-shape': 'rectangle',
                                                'text-background-padding': '3px',
                                                'font-size': 20}}
                        updated_stylesheet = selected_stylesheet + [style_with_label] + [style_node_clicked] + [
                            style_edge_label]
                        return updated_stylesheet, wstyle, left_style, right_style
                    else:
                        pass
            else:  # edgeがクリックされなければ
                updated_stylesheet = selected_stylesheet + [style_with_label] + [style_node_clicked]
                return updated_stylesheet, wstyle, left_style, right_style
        else:  # ノードがクリックされてなかったら
            left_style = {'width': '100%'}
            right_style = {'width': '0%'}
            if edge_data_dict:  # edgeがクリックされたら
                source_info_list = table.format_data_interface(
                    edge_data_dict['source'])  # sourceのインターフェース情報を取得
                for source_info in source_info_list:
                    # srcportと同じインターフェースだったら(cdpの出力はインターフェース名にスペース入ってるのでreplaceで消す)
                    if source_info['Port'] == edge_data_dict['srcport'].replace(' ', ''):
                        # エッジの太さ変更とラベル表示(Vlan情報)
                        style_edge_label = {'selector': '#' + edge_data_dict['id'],
                                            'style': {
                                                'width': 10,
                                                'label': 'Vlan' + source_info['Vlan'],
                                                'text-background-color': 'white',
                                                'text-background-opacity': 0.9,
                                                'text-background-shape': 'rectangle',
                                                'text-background-padding': '3px',
                                                'font-size': 20}}
                        updated_stylesheet = selected_stylesheet + [style_with_label] + [style_edge_label]
                        return updated_stylesheet, wstyle
            else:  # edgeがクリックされなければ
                updated_stylesheet = selected_stylesheet + [style_with_label]
                return updated_stylesheet, wstyle, left_style, right_style
    else:  # ノードにマウスがかざされていないとき
        left_style = {'width': '100%'}
        right_style = {'width': '0%'}
        if edge_data_dict:  # edgeがクリックされたら
            source_info_list = table.format_data_interface(edge_data_dict['source'])  # sourceのインターフェース情報を取得
            for source_info in source_info_list:
                # srcportと同じインターフェースだったら(cdpの出力はインターフェース名にスペース入ってるのでreplaceで消す)
                if source_info['Port'] == edge_data_dict['srcport'].replace(' ', ''):
                    # エッジの太さ変更とラベル表示(Vlan情報)
                    style_edge_label = {'selector': '#' + edge_data_dict['id'],
                                        'style': {
                                            'width': 10,
                                            'label': 'Vlan' + source_info['Vlan'],
                                            'text-background-color': 'white',
                                            'text-background-opacity': 0.9,
                                            'text-background-shape': 'rectangle',
                                            'text-background-padding': '3px',
                                            'font-size': 20}}
                    edge_updated_stylesheet = selected_stylesheet + [style_edge_label]
                    return edge_updated_stylesheet, wstyle, left_style, right_style
                else:
                    pass
        else:  # 何も起きていなければ
            return selected_stylesheet, wstyle, left_style, right_style


# 物理図上でクリックしたノードの各種情報を表示するコールバック関数
@app.callback(
    Output('table_p', 'children'),  # 出力先IDとしてright_partのidを指定
    Output('table_title_p', 'children'),
    Output('command_dropdown_p', 'style'),
    [Input('graph_p', 'tapNodeData')],  # クリックされたノードのデータ辞書を受け取る
    [Input('command_dropdown_p', 'value')]  # ドロップダウンで選択されたコマンドを受け取る
)
def show_command_dropdown(clicked_node_physical, command):
    if clicked_node_physical:
        clicked_node_name = clicked_node_physical['id']
        table_ttl = clicked_node_name  # テーブルエリアのトップに表示するノード名
        dropdown_style = {'visibility': 'visible'}

        if command == 'port':
            table_data = table.make_table_interface(table.format_data_interface(clicked_node_physical['id']))
        elif command == 'mac':
            table_data = table.make_table_mac(table.format_data_mac(clicked_node_physical['id']))
        elif command == 'route':
            table_data = table.make_table_iproute(table.format_data_iproute(clicked_node_physical['id']))
        elif command == 'ip_int':
            table_data = table.make_table_ip_int(table.format_data_ip_int(clicked_node_physical['id']))
        # elif command == 'run':
        #   table_data = table.make_table_run(table.format_data_run(node['id']))
        else:
            table_data = table.make_table_interface(table.format_data_interface(clicked_node_physical['id']))

        # タイトル、ドロップダウン、sh interfaces statusの出力を返す
        return table_data, table_ttl, dropdown_style
    else:  # ノードがクリックされていない時はコールバックの更新を停止
        raise dash.exceptions.PreventUpdate


# 論理図上でクリックしたノードの各種情報を表示するコールバック関数
@app.callback(
    Output('table_l', 'children'),  # 出力先IDとしてright_partのidを指定
    Output('table_title_l', 'children'),
    Output('command_dropdown_l', 'style'),
    [Input('graph_l', 'tapNodeData')],  # クリックされたノードのデータ辞書を受け取る
    [Input('command_dropdown_l', 'value')]  # ドロップダウンで選択されたコマンドを受け取る
)
def show_command_dropdown(clicked_node_logical, command):
    if clicked_node_logical:
        clicked_node_name = clicked_node_logical['id']
        table_ttl = clicked_node_name  # テーブルエリアのトップに表示するノード名
        dropdown_style = {'visibility': 'visible'}

        if command == 'port':
            table_data = table.make_table_interface(table.format_data_interface(clicked_node_logical['id']))
        elif command == 'mac':
            table_data = table.make_table_mac(table.format_data_mac(clicked_node_logical['id']))
        elif command == 'route':
            table_data = table.make_table_iproute(table.format_data_iproute(clicked_node_logical['id']))
        elif command == 'ip_int':
            table_data = table.make_table_ip_int(table.format_data_ip_int(clicked_node_logical['id']))
        # elif command == 'run':
        #   table_data = table.make_table_run(table.format_data_run(node['id']))
        else:
            table_data = table.make_table_interface(table.format_data_interface(clicked_node_logical['id']))

        # タイトル、ドロップダウン、sh interfaces statusの出力を返す
        return table_data, table_ttl, dropdown_style
    else:  # ノードがクリックされていない時はコールバックの更新を停止
        raise dash.exceptions.PreventUpdate
