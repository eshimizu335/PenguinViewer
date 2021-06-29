import dash_html_components as html
from app import app
from layouts import graph, access_time, theme_dropdown
import callbacks

# レイアウトのインデックス
app.layout = html.Div(
    children=[
        html.H1('Penguin Viewer'),
        theme_dropdown,
        html.H2(access_time[0:4] + '/' + access_time[4:6] + '/' + access_time[6:8] + ' ' + access_time[9:11] + ':' + access_time[11:13] + 'のネットワーク図'),
        html.Div(graph)],
    id='html',
    style={'backgroundColor': '#D7EEFF',
           'display': 'block',
           'overflow-x': 'scroll',
           'white-space': 'nowrap'})

if __name__ == '__main__':
    app.run_server(debug=False)
