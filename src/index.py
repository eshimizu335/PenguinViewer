import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from layouts import layout_p, layout_l
import callbacks

# レイアウトのインデックス
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Callbackでエラーにならないようにアプリケーションに登場するすべてのレイアウトを書いておく
app.validation_layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    layout_p,
    layout_l,
])


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/apps/physical':
        return layout_p
    elif pathname == '/apps/logical':
        return layout_l
    else:
        return '404'


if __name__ == '__main__':
    app.run_server(debug=True)
