# ssh each node, send commands and generate a JSON file from the outputs.
import configparser as cp
import datetime as dt
import json
from netmiko.ssh_autodetect import SSHDetect
from netmiko.ssh_dispatcher import ConnectHandler
import pandas as pd
import sys

from textfsm import TextFSMError

config = cp.ConfigParser()
config.read('./config.ini', encoding='utf-8')
input_folder = config.get('ssh', 'input_folder')
output_folder = config.get('ssh', 'output_folder')
list_filename = config.get('ssh', 'list_filename')
ssh_domain_name = config.get('ssh', 'ssh_domain_name')
nodes_path = input_folder + list_filename
nodes_dict_list = list()
from_list = list()
to_list = list()
nodes_list = list()
edges_list = list()
time_now = dt.datetime.now()
file_name = time_now.strftime('%Y%M%D_%H%M') + '.json'


def run_ssh():
    with open(nodes_path) as nf:
        header = next(nf)  # skip header
        for line in nf:
            nodes_info_list = [x.strip() for x in line.split(',')]
            nodes_dict_temp = {'device_type': nodes_info_list[0],
                               'host': nodes_info_list[1],
                               'username': nodes_info_list[2],
                               'password': nodes_info_list[3]}
            nodes_dict_list.append(nodes_dict_temp)

    # access each node
    for node in nodes_dict_list:
        # device type detection
        guesser = SSHDetect(**node)
        best_match = guesser.autodetect()

        # set device type
        node['device_type'] = best_match
        connection = ConnectHandler(**node)

        # get hostsname, model and macaddr from the output of "show version" command.
        output_v = connection.send_command('show version', use_textfsm=True)
        df_v = pd.DataFrame(output_v)
        version_dict = df_v.to_dict(orient='records')
        hostname = version_dict[0]['hostname']
        from_list.append(hostname)
        try:
            macaddr = version_dict[0]['mac'][0]
        except IndexError:
            macaddr = 'no macaddr found.'
        model = version_dict[0]['hardware'][0]

        # get vtp domain and vtp mode from the output of "show vtp status" command.
        output_vtp = connection.send_command('show vtp status', use_textfsm=True)
        df_vtp = pd.DataFrame(output_vtp)
        vtp_dict = df_vtp.to_dict(orient='records')
        vtp_domain = vtp_dict[0]['domain']
        vtp_mode = vtp_dict[0]['mode']

        # get interfaces' status.
        ist_list = []
        output_ist = connection.send_command('show interfaces status', use_textfsm=True)
        df_ist = pd.DataFrame(output_ist)
        ist_dict = df_ist.to_dict(orient='records')
        for i in ist_dict:
            print(i)
            ist_data = {'Port': i['port'], 'Description': i['name'], 'Status': i['status'], 'Vlan': i['vlan'],
                        'Duplex': i['duplex'], 'Speed': i['speed'], 'Type': i['type']}
            ist_list.append(ist_data)

        # get arp table.
        arp_list = []
        output_arp = connection.send_command('show ip arp', use_textfsm=True)
        df_arp = pd.DaraFrame(output_arp)
        arp_dict = df_arp.to_dict(orient='records')
        for arp in arp_dict:
            arp_data = {'Protocol': arp['protocol'], 'Address': arp['address'], 'Age': arp['age'], 'Mac': arp['mac'],
                        'Type': arp['type'], 'Interface': arp['interface']}
            arp_list.append(arp_data)

        # get mac-address table.
        mac_list = []
        try:
            output_mac = connection.send_command('show mac address-table', use_textfsm=True)
            df_mac = pd.DaraFrame(output_mac)
            mac_dict = df_mac.to_dict(orient='records')
            for mac in mac_dict:
                mac_data = {'Dst_addr': mac['destination_address'], 'Type': mac['type'], 'Vlan': mac['vlan'],
                            'Dst_port': mac['destination_port']}
                mac_list.append(mac_data)
        except TextFSMError:
            mac_data = {'Dst_addr': 'cannot detect', 'Type': 'cannot detect', 'Vlan': 'cannot detect',
                        'Dst_port': 'cannot detect'}
            mac_list.append(mac_data)

        # get routing table.
        route_list = []
        output_route = connection.send_command('show ip route', use_textfsm=True)
        df_route = pd.DataFrame(output_route)
        route_dict = df_route.to_dict(orient='records')
        for route in route_dict:
            route_data = {'Protocol': route['protocol'], 'Type': route['type'], 'Network': route['network'],
                          'Mask': route['mask'], 'Distance': route['distance'], 'Metric': route['metric'],
                          'Nexthop_ip': route['nexthop_ip'],
                          'Nexthop_if': route['nexthop_if'], 'Uptime': route['uptime']}
            route_list.append(route_data)

        # get ip interface information.
        ipint_list = []
        output_ipint = connection.send_command('show ip interface brief', use_textfsm=True)
        df_ipint = pd.DataFrame(output_ipint)
        ipint_dict = df_ipint.to_dict(orient='records')
        for ipint in ipint_dict:
            ipint_data = {'Intf': ipint['intf'], 'Ipaddr': ipint['ipaddr'], 'Status': ipint['status'],
                          'Proto': ipint['proto']}
            ipint_list.append(ipint_data)

        # get cdp neighbors.
        cdp_list = []
        output_c = connection.send_command('show cdp neighbors', use_textfsm=True)
        try:
            df_c = pd.DataFrame(output_c)
        except ValueError:  # no cdp entry
            pass
        else:
            cdp_dict = df_c.to_dict(orient='records')
            for cdp in cdp_dict:
                cdp_data = {'Neighbor': cdp['neighbor'], 'Local_interface': cdp['local_interface'],
                            'Capability': cdp['capability'], 'Platform': cdp['platform'],
                            'Neighbor_interface': cdp['neighbor_interface']}
                cdp_list.append(cdp_data)
                # add neighbors to the node list.
                nodes_list.append({'data': {'id': cdp['neighbor'], 'label': cdp['neighbor'], 'model': cdp['platform']}})
                # edge data
                edges_list.append({
                    'data': {'id': hostname + '---' + cdp['neighbor'],
                             'source': hostname,
                             'target': cdp['neighbor']
                             },
                })

        # add the node to the node list.
        nodes_list.append({'data': {'id': hostname, 'label': hostname, 'ipaddr': node['host'], 'macaddr': macaddr,
                                    'model': model, 'vtp_domain': vtp_domain, 'vtp_mode': vtp_mode, 'cdp': cdp_list,
                                    'interface_status': ist_list, 'ip_arp': arp_list, 'mac_table': mac_list,
                                    'ip_route': route_list, 'int_brief': ipint_list}})

        # disconnect from the node.
        connection.disconnect()

        # 作ったデータをjsonに書き出し

    with open(output_folder + file_name, 'w') as gf:
        json.dump(nodes_list + edges_list, gf, indent=4)


if __name__ == '__main__':
    run_ssh()
