from dash.dependencies import Input, Output
from app import app

from layouts import default_stylesheet, universe_stylesheet, flower_stylesheet


# ドロップダウンでスタイルを変更し、マウスをかざしたノードの機種名を表示する
@app.callback(
    Output('graph', 'stylesheet'),  # グラフ部分のスタイル
    Output('html', 'style'),  # ページ全体のスタイル
    [Input('theme_dropdown', 'value')],  # ドロップダウンで選択されたデザインの種類
    [Input('graph', 'mouseoverNodeData')],  # マウスをかざしたノードのデータ辞書を受け取る
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
