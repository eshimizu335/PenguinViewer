import dash_html_components as html
from app import app
from layouts import graph, access_time, theme_dropdown
import callbacks_2
from layouts import layout_html

# レイアウトのインデックス
app.layout = layout_html

if __name__ == '__main__':
    app.run_server(debug=False)
