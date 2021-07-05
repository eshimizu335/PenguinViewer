import dash
# import dash_auth

app = dash.Dash(__name__, title='Penguin Viewer')
app.config.suppress_callback_exceptions = True

server = app.server

