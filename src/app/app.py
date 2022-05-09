import configparser as cp
import eel
import json
import os
import pathlib

assets_folder = './assets/'
config = cp.ConfigParser()
config.read('./app_config.ini')
output_folder = config.get('settings', 'path')

# Find the latest JSON file.
output_files = list(pathlib.Path(output_folder).glob('*'))
file_updates = {file_path: os.stat(file_path).st_mtime for file_path in output_files}
latest_file = max(file_updates, key=file_updates.get)


# Get the access time from the latest output file name.
# "@eel.expose" makes it possible to call Python functions from JavaScript.
@eel.expose
def get_access_time():
    file_name = os.path.basename(latest_file)  # Get the access time from the JSON file name.
    access_time = {'access_year': file_name[0:4], 'access_month': file_name[4:6], 'access_date': file_name[6:8],
                   'access_hour': file_name[9:11], 'access_minute': file_name[11:13]}
    return access_time


@eel.expose
def generate_graph_data(file=latest_file):  # set the latest file as a default file
    latest_graph = open(file, 'r')
    graph_data = json.load(latest_graph)
    return graph_data


@eel.expose
def define_graph_style(theme):
    # JSON files which define the graph style.
    if theme == 'default':
        json_open = open(assets_folder + 'default.json')
    elif theme == 'universe':
        json_open = open(assets_folder + 'universe.json')
    elif theme == 'flower':
        json_open = open(assets_folder + 'flower.json')
    else:
        json_open = open(assets_folder + 'default.json')

    json_load = json.load(json_open)

    # Variables for graph style
    common_style = [
        {
            'selector': 'node',
            'style': {
                'content': 'data(id)'
            }
        },
        {
            'selector': 'edge',
            'style': {
                'source-label': 'data(srcport)',
                'target-label': 'data(dstport)'
            }
        }
    ]

    # Stylesheet for the graph
    graph_stylesheet = common_style + json_load

    return graph_stylesheet


def start():
    eel.init('web', allowed_extensions=['.js', '.html', '.css'])
    eel.start('html/index.html', port=9201)


if __name__ == '__main__':
    start()
