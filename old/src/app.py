import dash
import dash_auth

app = dash.Dash(__name__, title='Penguin Viewer')
app.config.suppress_callback_exceptions = True
server = app.server
# for i in auth_list:
#   auth = dash_auth.BasicAuth(app, i)

pair = {'admin': 'admin'}
auth = dash_auth.BasicAuth(app, pair)
