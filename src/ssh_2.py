# 各スイッチにSSH接続し、取得した出力からホスト名のリストを生成する。
# vtp statusも取得する。

import datetime as dt
import json
import pandas as pd
import netmiko
from netmiko.ssh_autodetect import SSHDetect
from netmiko.ssh_dispatcher import ConnectHandler

input_folder = '../input/'
output_folder = '../output/'
nodes_path = input_folder + '.nodes.csv'
nodes_dict_list = list()  # SSH接続に必要な情報を辞書としてノードごとに定義しリスト化
from_list = list()
to_list = list()
nodes_list = list()  # 描画用のノードリスト
edges_list = list()  # 描画用のエッジリスト
password = input('password? ')  # とりあえずパスワードはコンソール入力
time_now = dt.datetime.now()  # タイムゾーンは選択できるようにする。そのうち。
file_name = time_now.strftime('%Y%m%d_%H%M') + '.json'

# 各ノードのSSH接続情報読み込み
with open(nodes_path) as nf:
    header = next(nf)  # ヘッダをスキップ
    for line in nf:
        # 一行のデータをカンマで分割してリスト化し、そこにstrip()で余分な空白を除去する
        nodes_info_list = [x.strip() for x in line.split(',')]
        nodes_dict_temp = {'device_type': nodes_info_list[0],
                           'host': nodes_info_list[1],
                           'username': nodes_info_list[2],
                           'password': password}  # ここのパスワードの埋め方は今後検討
        nodes_dict_list.append(nodes_dict_temp)

# 各ノードにリモートアクセス
for node in nodes_dict_list:
    # 自動検出
    guesser = SSHDetect(**node)
    best_match = guesser.autodetect()

    # 検出結果のデバッグ出力
    print('device_type:' + best_match)

    # 自動検出したdevice_typeを再設定する
    node['device_type'] = best_match
    connection = ConnectHandler(**node)

    # show versionコマンド実行結果(output_v)をDataFrameに変換してホスト名と機種名のみ取得
    output_v = connection.send_command('show version', use_textfsm=True)
    df_v = pd.DataFrame(output_v)
    version_dict = df_v.to_dict(orient='records')
    hostname = version_dict[0]['hostname']
    from_list.append(hostname)  # 描画対象ノードリストに追加
    model = version_dict[0]['hardware'][0]  # hardwareはリストで取得してる(textfsm)
    print(from_list)

    # show vtp statusコマンド実行結果(output_vtp)をDataFrameに変換してvtp domainとvtp modeのみ取得
    output_vtp = connection.send_command('show vtp status', use_textfsm=True)
    df_vtp = pd.DataFrame(output_vtp)
    vtp_dict = df_vtp.to_dict(orient='records')
    vtp_domain = vtp_dict[0]['domain']
    vtp_mode = vtp_dict[0]['mode']

    # ノード・エッジデータ作成
    nodes_list.append({'data': {'id': hostname, 'label': hostname, 'model': model, 'vtp_domain':vtp_domain, 'vtp_mode':vtp_mode}})  # まずは自分を追加

    # show cdp neighborsコマンド実行結果(ouput_c)をDataFrameに変換してネイバー名とネイバーの機種名のみ取得し描画対象ノードリストに追加
    output_c = connection.send_command('show cdp neighbors', use_textfsm=True)
    print(output_c)
    try:
        df_c = pd.DataFrame(output_c)
    except ValueError:
        print('no cdp entry.')
    else:
        cdp_dict = df_c.to_dict(orient='records')
        for cdp in cdp_dict:  # ここからネイバーを追加
            nodes_list.append({'data': {'id': cdp['neighbor'], 'label': cdp['neighbor'], 'model': cdp['platform']}})
            edges_list.append({
                # srcportとdstportは独自キー
                'data': {
                    'source': hostname,
                    'target': cdp['neighbor']
                },
            })

    # 切断
    connection.disconnect()

    # 作ったデータをjsonに書き出し

    with open(output_folder + file_name, 'w') as gf:
        json.dump(nodes_list + edges_list, gf, indent=4)
