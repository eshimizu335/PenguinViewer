import dash
import dash_table
from read import get_command_output


def format_data_interface(node_hostname):
    data_list_1 = []
    if_list = get_command_output(node_hostname, 'port')
    for i in if_list:
        temp_list = [i['PORT'], i['NAME'], i['STATUS'], i['VLAN'], i['DUPLEX'], i['SPEED'],
                     i['TYPE']]  # なぜか直接辞書に入れるとエラーになるのでいったんリストに入れる
        if_data = {'Port': temp_list[0], 'Description': temp_list[1], 'Status': temp_list[2], 'Vlan': temp_list[3],
                   'Duplex': temp_list[4], 'Speed': temp_list[5], 'Type': temp_list[6]}
        data_list_1.append(if_data)

    return data_list_1


def format_data_mac(node_hostname):
    data_list_3 = []
    mac_list = get_command_output(node_hostname, 'mac')
    for i in mac_list:
        temp_list = [i['DESTINATION_ADDRESS'], i['TYPE'], i['VLAN'], i['DESTINATION_PORT']]
        mac_data = {'Dst_addr': temp_list[0], 'Type': temp_list[1], 'Vlan': temp_list[2], 'Dst_port': temp_list[3], }
        data_list_3.append(mac_data)

    return data_list_3


def format_data_iproute(node_hostname):
    data_list_5 = []
    ir_list = get_command_output(node_hostname, 'route')
    for i in ir_list:
        temp_list = [i['PROTOCOL'], i['TYPE'], i['NETWORK'], i['MASK'], i['DISTANCE'], i['METRIC'],
                     i['NEXTHOP_IP'], i['NEXTHOP_IF'], ['UPTIME']]  # なぜか直接辞書に入れるとエラーになるのでいったんリストに入れる
        ir_data = {'Protocol': temp_list[0], 'Type': temp_list[1], 'Network': temp_list[2], 'Mask': temp_list[3],
                   'Distance': temp_list[4], 'Metric': temp_list[5], 'Nexthop_ip': temp_list[6],
                   'Nexthop_if': temp_list[7], 'Uptime': temp_list[8]}
        data_list_5.append(ir_data)

    return data_list_5


def format_data_ip_int(node_hostname):
    data_list_7 = []
    ip_int__list = get_command_output(node_hostname, 'ip_int')
    for i in ip_int__list:
        temp_list = [i['INTF'], i['IPADDR'], i['STATUS'], i['PROTO']]
        mac_data = {'Intf': temp_list[0], 'Ipaddr': temp_list[1], 'Status': temp_list[2], 'Proto': temp_list[3], }
        data_list_7.append(mac_data)

    return data_list_7


def make_table_interface(data_list_2):
    app = dash.Dash(__name__)
    app.layout = dash_table.DataTable(
        # columnsにデータを渡す
        columns=[
            {'name': 'Port', 'id': 'Port'},
            {'name': 'Description', 'id': 'Description'},
            {'name': 'Status', 'id': 'Status'},
            {'name': 'Vlan', 'id': 'Vlan'},
            {'name': 'Duplex', 'id': 'Duplex'},
            {'name': 'Speed', 'id': 'Speed'},
            {'name': 'Type', 'id': 'Type'}
        ],
        # dataにデータを渡す
        # dataのキーとcolumnsのidが一致するように！
        data=data_list_2,
        # テーブルを画面いっぱいに広げるかどうか
        fill_width=False,  # 広げない
        style_cell={'fontSize': 18, 'textAlign': 'center'},
        style_header={'background-color': '#D7EEFF'}  # テーブルヘッダのスタイル
    )

    return app.layout


def make_table_mac(data_list_4):
    app = dash.Dash(__name__)
    app.layout = dash_table.DataTable(
        # columnsにデータを渡す
        columns=[
            {'name': 'Dst_addr', 'id': 'Dst_addr'},
            {'name': 'Type', 'id': 'Type'},
            {'name': 'Vlan', 'id': 'Vlan'},
            {'name': 'Dst_port', 'id': 'Dst_port'},
        ],
        # dataにデータを渡す
        # dataのキーとcolumnsのidが一致するように！
        data=data_list_4,
        # テーブルを画面いっぱいに広げるかどうか
        fill_width=False,  # 広げない
        style_cell={'fontSize': 18, 'textAlign': 'center'},
        style_header={'background-color': '#D7EEFF'}  # テーブルヘッダのスタイル
    )

    return app.layout


def make_table_iproute(data_list_6):
    app = dash.Dash(__name__)
    app.layout = dash_table.DataTable(
        # columnsにデータを渡す
        columns=[
            {'name': 'Protocol', 'id': 'Protocol'},
            {'name': 'Type', 'id': 'Type'},
            {'name': 'Network', 'id': 'Network'},
            {'name': 'Mask', 'id': 'Mask'},
            {'name': 'Distance', 'id': 'Distance'},
            {'name': 'Metric', 'id': 'Metric'},
            {'name': 'Nexthop_ip', 'id': 'Nexthop_ip'},
            {'name': 'Nexthop_if', 'id': 'Nexthop_if'},
            {'name': 'Uptime', 'id': 'Uptime'},
        ],
        # dataにデータを渡す
        # dataのキーとcolumnsのidが一致するように！
        data=data_list_6,
        # テーブルを画面いっぱいに広げるかどうか
        fill_width=False,  # 広げない
        style_cell={'fontSize': 18, 'textAlign': 'center'},
        style_header={'background-color': '#D7EEFF'}  # テーブルヘッダのスタイル
    )

    return app.layout


def make_table_ip_int(data_list_8):
    app = dash.Dash(__name__)
    app.layout = dash_table.DataTable(
        # columnsにデータを渡す
        columns=[
            {'name': 'Intf', 'id': 'Intf'},
            {'name': 'Ipaddr', 'id': 'Ipaddr'},
            {'name': 'Status', 'id': 'Status'},
            {'name': 'Proto', 'id': 'Proto'},
        ],
        # dataにデータを渡す
        # dataのキーとcolumnsのidが一致するように！
        data=data_list_8,
        # テーブルを画面いっぱいに広げるかどうか
        fill_width=False,  # 広げない
        style_cell={'fontSize': 18, 'textAlign': 'center'},
        style_header={'background-color': '#D7EEFF'}  # テーブルヘッダのスタイル
    )

    return app.layout
