import glob
import pandas as pd

import textfsm

input_folder = '../input/'  # スイッチの出力置き場
# edgeのデータフレームに格納するリストの作成
from_list = []
to_list = []
srcport_list = []
dst_port_list = []


def get_core_information():
    """コアスイッチの情報を取得する"""
    global input_folder
    # コアスイッチの情報取得
    core_primary_hostname = input('core_primary_hostname? ')
    core_secondary_hostname = core_primary_hostname.split('-')[0] + '-2'
    core_primary_cdp_path = glob.glob(input_folder + core_primary_hostname + '_cdp.*')[0]
    core_info = {'hostname': core_primary_hostname, 'cdp_path': core_primary_cdp_path}
    return core_primary_hostname, core_secondary_hostname, core_info


def read_cdp(switch_info, skip_switch):
    """show cdp neighborsの出力を読み込む"""
    global input_folder
    global from_list
    global to_list
    global srcport_list
    global dst_port_list

    skip_switch.append(switch_info['hostname'])  # 自分を既出スイッチリストに加える

    # show cdp neighborsの出力を読み込む
    with open(switch_info['cdp_path']) as cf:
        cdp_text = cf.read()

    # IOSのテンプレート
    template_path = '../templates/cisco_ios_show_cdp_neighbors.textfsm'

    # fsmで結果を解析、抽出
    with open(template_path) as f:
        fsm = textfsm.TextFSM(f)
    output = fsm.ParseText(cdp_text)

    # 解析結果をDataFrameに変換
    df = pd.DataFrame(output, columns=fsm.header)

    # DataFrameを辞書のリストに変換する
    neighbor_dict_list = df.to_dict(orient='records')  # ネイバー一台の情報が辞書。その辞書が複数行あるのでリスト。
    for neighbor_dict in neighbor_dict_list:  # 各ネイバーについての処理
        if neighbor_dict['NEIGHBOR'] in skip_switch:  # 既出スイッチはスキップ
            pass
        else:
            # まずは描画用の4つのリストに値を追加
            from_list.append(switch_info['hostname'])  # 自分(ネイバーではない！)のホスト名を入れる
            to_list.append(neighbor_dict['NEIGHBOR'])  # ネイバーのホスト名を入れる
            srcport_list.append(neighbor_dict['LOCAL_INTERFACE'])
            dst_port_list.append(neighbor_dict['NEIGHBOR_INTERFACE'])

    # 再帰的にこの関数を呼び出すため、引数としてネイバーの辞書を作り直す
    # 以下を上のループに入れてしまうと幾つかの必要なノードがスキップされてしまうのでもう一度ここでループやり直す
    for neighbor_dict in neighbor_dict_list:
        if neighbor_dict['NEIGHBOR'] in skip_switch:  # 既出スイッチはスキップ
            pass
        else:
            neighbor_dict_arg = {'hostname': neighbor_dict['NEIGHBOR'],
                                 'cdp_path': glob.glob(input_folder + neighbor_dict['NEIGHBOR'] + '_cdp.*')[0]}
            read_cdp(neighbor_dict_arg, skip_switch)

    return from_list, to_list, srcport_list, dst_port_list


def check_model(host):
    global input_folder
    with open(glob.glob(input_folder + host + '_version.*')[0]) as vf:
        version_text = vf.read()

        tmp_vf_list = version_text.split('\n')
        # IOSのテンプレート
        template_path = '../templates/cisco_ios_show_version.textfsm'

    # fsmで結果を解析、抽出
    with open(template_path) as f:
        fsm = textfsm.TextFSM(f)
    output = fsm.ParseText(version_text)

    # 解析結果をDataFrameに変換
    df = pd.DataFrame(output, columns=fsm.header)

    version_dict = df.to_dict(orient='records')
    model_name = version_dict[0]['HARDWARE'][0]

    return model_name


def get_command_output(hostname, command):
    global input_folder
    if command == 'port':
        file_name = '_if_status.*'
        template_path = '../templates/cisco_ios_show_interfaces_status.textfsm'
    elif command == 'mac':
        file_name = '_mac.*'
        template_path = '../templates/cisco_ios_show_mac-address-table.textfsm'
    elif command == 'route':
        file_name = '_ip_route.*'
        template_path = template_path = '../templates/cisco_ios_show_ip_route.textfsm'
    elif command == 'ip_int':
        file_name = '_ip_int.*'
        template_path = '../templates/cisco_ios_show_ip_interface_brief.textfsm'
    # elif command == 'run':
    elif command == 'switch_port':
        file_name = '_switch_port.*'
        template_path = '../templates/cisco_ios_show_interfaces_switchport.textfsm'
    else:
        file_name = '_if_status.*'
        template_path = '../templates/cisco_ios_show_interfaces_status.textfsm'

    with open(glob.glob(input_folder + hostname + file_name)[0]) as file:
        file_text = file.read()
        tmp_list = file_text.split('\n')

    # fsmで結果を解析、抽出
    with open(template_path) as f:
        fsm = textfsm.TextFSM(f)
    output = fsm.ParseText(file_text)

    # 解析結果をDataFrameに変換
    df = pd.DataFrame(output, columns=fsm.header)

    data_dict = df.to_dict(orient='records')
    return data_dict


def get_cable_type(hostname2, if_list):
    source_info_list = get_command_output(hostname2, 'int_status')
    # インターフェースごとのTYPE情報の辞書を作る
    cable = []
    for source_info in source_info_list:
        if source_info['PORT'] in if_list:
            if source_info['TYPE'] in ['10/100BaseTX', '10GBASE-T']:
                source_cable_type = 'utp'
            else:
                source_cable_type = 'fiber'
            cable.append(source_cable_type)
        else:
            pass
    return cable


def get_port_info(hostname3, if_list):
    source_info_list_2 = get_command_output(hostname3, 'switch_port')
    # インターフェースごとのモード情報の辞書を作る
    port = []
    for source_info_2 in source_info_list_2:
        if source_info_2['INTERFACE'] in if_list:
            port_mode = source_info_2['ADMIN_MODE']
            port.append(port_mode)
        else:
            pass
    return port
