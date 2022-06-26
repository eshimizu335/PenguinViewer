# ssh each node, send commands and generate a JSON file from the outputs.
import configparser as cp
import datetime as dt
import json

import pandas as pd
from netmiko.ssh_autodetect import SSHDetect
from netmiko.ssh_dispatcher import ConnectHandler
from textfsm import TextFSMError

config = cp.ConfigParser()
config.read('./ssh_config.ini', encoding='utf-8')
input_folder = config.get('ssh', 'input_folder')
output_folder = config.get('ssh', 'output_folder')
list_filename = config.get('ssh', 'list_filename')

ssh_domain_name = config.get('ssh', 'domain_name')
nodes_path = input_folder + list_filename
nodes_dict_list = list()
router_ip_list = list()  # IP list for devices with multiple IP addresses
nodes_list = list()
edges_list = list()
hostnames = dict()
neighbors = dict()
neighbor_list = list()
time_now = dt.datetime.now()
file_name = time_now.strftime('%Y%M%D_%H%M') + '.json'


def read_nodes_list():
    """read the nodes list."""
    with open(nodes_path) as nf:
        header = next(nf)  # skip header
        for line in nf:
            nodes_info_list = [x.strip() for x in line.split(',')]
            node_info_dict = {
                'device_type': nodes_info_list[0],
                'host': nodes_info_list[1],
                'username': nodes_info_list[2],
                'password': nodes_info_list[3]
            }
            nodes_dict_list.append(node_info_dict)


def get_version(connection):
    """run "show version" command and get the node's hostname, model and MAC address from the output."""
    output_v = connection.send_command('show version', use_textfsm=True)
    df_v = pd.DataFrame(output_v)
    version_dict = df_v.to_dict(orient='records')
    hostname = version_dict[0]['hostname']
    try:
        macaddr = version_dict[0]['mac'][0]
    except IndexError:
        macaddr = 'no macaddr found.'
    model = version_dict[0]['hardware'][0]
    return hostname, macaddr, model


def get_vtp(connection):
    """run "show vtp status" command and get the node's vtp domain and vtp mode from the output."""
    output_vtp = connection.send_command('show vtp status', use_textfsm=True)
    df_vtp = pd.DataFrame(output_vtp)
    vtp_dict = df_vtp.to_dict(orient='records')
    vtp_domain = vtp_dict[0]['domain']
    vtp_mode = vtp_dict[0]['mode']
    return vtp_domain, vtp_mode


def get_interfaces_status(connection):
    """run "show interfaces status" command and get the node's interfaces' status from the output."""
    ist_list = []
    try:
        output_ist = connection.send_command('show interfaces status', use_textfsm=True)
        df_ist = pd.DataFrame(output_ist)
        ist_dict = df_ist.to_dict(orient='records')
        for i in ist_dict:
            print(i)
            ist_data = {
                'Port': i['port'],
                'Description': i['name'],
                'Status': i['status'],
                'Vlan': i['vlan'],
                'Duplex': i['duplex'],
                'Speed': i['speed'],
                'Type': i['type']
            }
            ist_list.append(ist_data)
    except TextFSMError:
        ist_data = {
            'Port': 'cannot detect',
            'Description': 'cannot detect',
            'Status': 'cannot detect',
            'Vlan': 'cannot detect',
            'Duplex': 'cannot detect',
            'Speed': 'cannot detect',
            'Type': 'cannot detect'
        }
        ist_list.append(ist_data)
    return ist_list


def get_arp(connection):
    """run "show ip arp" command and get the node's arp table from the output."""
    arp_list = []
    output_arp = connection.send_command('show ip arp', use_textfsm=True)
    df_arp = pd.DaraFrame(output_arp)
    arp_dict = df_arp.to_dict(orient='records')
    for arp in arp_dict:
        arp_data = {
            'Protocol': arp['protocol'],
            'Address': arp['address'],
            'Age': arp['age'],
            'Mac': arp['mac'],
            'Type': arp['type'],
            'Interface': arp['interface']
        }
        arp_list.append(arp_data)
    return arp_list


def get_mac_list(connection):
    """run "show mac address-table" command and get the node's get mac-address table from the output."""
    mac_list = []
    try:
        output_mac = connection.send_command('show mac address-table', use_textfsm=True)
        df_mac = pd.DaraFrame(output_mac)
        mac_dict = df_mac.to_dict(orient='records')
        for mac in mac_dict:
            mac_data = {
                'Dst_addr': mac['destination_address'],
                'Type': mac['type'],
                'Vlan': mac['vlan'],
                'Dst_port': mac['destination_port']
            }
            mac_list.append(mac_data)
    except TextFSMError:
        mac_data = {
            'Dst_addr': 'cannot detect',
            'Type': 'cannot detect',
            'Vlan': 'cannot detect',
            'Dst_port': 'cannot detect'
        }
        mac_list.append(mac_data)
    return mac_list


def get_ip_route(connection):
    """run "show ip route" command and get the node's routing table from the output."""
    route_list = []
    output_route = connection.send_command('show ip route', use_textfsm=True)
    df_route = pd.DataFrame(output_route)
    route_dict = df_route.to_dict(orient='records')
    for route in route_dict:
        route_data = {
            'Protocol': route['protocol'],
            'Type': route['type'],
            'Network': route['network'],
            'Mask': route['mask'],
            'Distance': route['distance'],
            'Metric': route['metric'],
            'Nexthop_ip': route['nexthop_ip'],
            'Nexthop_if': route['nexthop_if'],
            'Uptime': route['uptime']
        }
        route_list.append(route_data)
    return route_list


def get_ip_interface_brief(connection):
    """run "show ip interface brief" command and get the node's ip interface information from the output."""
    ipint_list = []
    output_ipint = connection.send_command('show ip interface brief', use_textfsm=True)
    df_ipint = pd.DataFrame(output_ipint)
    ipint_dict = df_ipint.to_dict(orient='records')
    for ipint in ipint_dict:
        ipint_data = {
            'Intf': ipint['intf'],
            'Ipaddr': ipint['ipaddr'],
            'Status': ipint['status'],
            'Proto': ipint['proto']
        }
        ipint_list.append(ipint_data)
    return ipint_list


def get_cdp(connection):
    """run "show cdp neighbors detail" command and get the node's cdp neighbors from the output."""
    cdp_list = []
    output_c = connection.send_command('show cdp neighbors detail', use_textfsm=True)
    try:
        df_c = pd.DataFrame(output_c)
    except ValueError:
        print('no cdp entry.')
    else:
        cdp_dict = df_c.to_dict(orient='records')
        for cdp in cdp_dict:
            cdp_hostname = cdp['destination_host']
            if '.' in cdp_hostname:  # delete domain name
                cdp_hostname = cdp_hostname[0:cdp_hostname.find('.')]
            cdp_srcport = cdp['local_port'].replace('Ethernet', 'Et').replace('FasEt', 'Fa').replace('GigabitEt',
                                                                                                     'Gi').replace(
                'TenGiEt', 'Te')
            cdp_dstport = cdp['remote_port'].replace('Ethernet', 'Et').replace('FasEt', 'Fa').replace('GigabitEt',
                                                                                                      'Gi').replace(
                'TenGiEt', 'Te')
            cdp_data = {
                'hostname': cdp_hostname,
                'ipaddr': cdp['management_ip'],
                'Local_interface': cdp_srcport,
                'capabilities': cdp['capabilities'],
                'platform': cdp['platform'],
                'Neighbor_interface': cdp_dstport
            }
            cdp_list.append(cdp_data)
    return cdp_list


def get_vlan(connection):
    """run "show vlan brief" command and get the node's vlan information from the output."""
    vlan_list = []
    vlan_class = []
    output_vlan = connection.send_command('show vlan brief', use_textfsm=True)
    df_vlan = pd.DataFrame(output_vlan)
    vlan_dict = df_vlan.to_dict(orient='records')
    for vlan in vlan_dict:
        vlan_data = {
            'id': vlan['vlan_id'],
            'name': vlan['name']
        }
        vlan_list.append('vlan' + str(vlan['vlan_id']))
    return vlan_list, vlan_class


def createNodesEdges(cdps_data, host_data):
    """create nodes and edges' data for cytoscape."""
    for cdp_data in cdps_data:  # add neighbors.
        cdp_id = 'node' + str(len(nodes_list))  # default node's ID
        # If the node has multiple IP addresses, its hostname will be the ID of the node.
        if cdp_data['ipaddr'] in router_ip_list:
            cdp_id = cdp_data['hostname']
        # If the node doesn't hove an IP address, its hostname + a sequential number will be the ID of the node.
        elif len(cdps_data['ipaddr']) == 0:
            cdp_id = cdp_data['hostname'] + str(len(nodes_list))
        else:  # generate the ID from the node's IP address.
            cdp_id = cdp_data['ipaddr'].replace('.', '')
        flag = True
        for index, node_item in enumerate(nodes_list):
            if node_item['data']['id'] == cdp_id:
                flag = False
                break
        print('get_index' + str(get_index('id', cdp_id) > -1))
        print('flag:' + str(flag))
        if flag:
            nodes_list.append({
                'group': 'nodes',
                'data': {
                    'id': cdp_id,
                    'label': cdp_data['hostname'],
                    'ipdaddr': cdp_data['ipaddr'],
                    'model': cdp_data['platform'],
                    'rank': host_data['rank'] + 1,
                    'connections': 1
                },
                'classes': ['nodes', 'neighbors']
            })
        # edges
        flag = True
        for index, edge_item in enumerate(edges_list):
            if (edge_item['data']['source'] + edge_item['data']['srcport'] == cdp_id + cdps_data[
                'Neighbor_interface'] and
                    edge_item['data']['target'] + edge_item['data']['dstport'] == host_data['id'] + cdps_data[
                        'Local_interface']):
                flag = False
                break
        if flag:
            edges_list.append({
                'group': 'egdes',
                'data': {
                    'id': 'edge' + str(len(edges_list)),
                    'source': host_data['id'],
                    'srchost': host_data['label'],
                    'srcport': cdp_data['Local_interface'],
                    'target': cdp_id,
                    'dsthost': cdp_data['hostname'],
                    'dstport': cdp_data['Neighbor_interface']
                },
                'classes': ['edge']
            })


def get_index(key, value):
    for index, node in enumerate(nodes_list):
        if node['data'][key] == value:
            return index
    return -1


def run_get_switch():
    read_nodes_list()
    for i, node in enumerate(nodes_dict_list):
        print(str(i + 1) + '/' + str(len(nodes_dict_list)) + '  ip:' + node['ip'] + '  type:' + node['device_type'])
        # Initialize the node's information.
        self_dict = {
            'group': 'nodes',
            'data': {
                'id': node['ip'].replace('.', ''),
                'label': node['ip'],
                'ipaddr': node['ip'],
                'model': '',
                'vtp_domain': '',
                'vtp_mode': '',
                'interface_status': '',
                'int_brief': '',
                'ip_arp': '',
                'ip_route': '',
                'mac_table': '',
                'vlan': '',
                'cdp': '',
                'rank': '',
                'connections': 0
            },
            'classes': ''
        }
        try:  # access each node
            # device type detection
            guesser = SSHDetect(**node)
            best_match = guesser.autodetect()

            # set device type
            node['device_type'] = best_match
            connection = ConnectHandler(**node)
        except Exception as e:
            print(e)
            self_dict['data']['rank'] = 9999
            self_dict['data']['connections'] = 0
            self_dict['classes'] = ['nodes', 'offline']
        else:
            host_id = hostname = macaddr = model = vtp_domain = vtp_mode = cdp_list = ''
            ist_list = arp_list = mac_list = route_list = ipint_list = vlan_list = vlan_classes = ''
            # get the node's information.
            hostname, macaddr, model = get_version(connection)
            self_dict['data']['label'] = hostname
            self_dict['data']['macaddr'] = macaddr
            self_dict['data']['model'] = model

            vtp_domain, vtp_mode = get_vtp(connection)
            self_dict['data']['vtp_domain'] = vtp_domain
            self_dict['data']['vtp_mode'] = vtp_mode

            ist_list = get_interfaces_status(connection)
            self_dict['data']['interface_status'] = ist_list

            arp_list = get_arp(connection)
            self_dict['data']['ip_arp'] = arp_list

            mac_list = get_mac_list(connection)
            self_dict['data']['mac_table'] = mac_list

            route_list = get_ip_route(connection)
            self_dict['data']['ip_route'] = route_list

            ipint_list = get_ip_interface_brief(connection)
            self_dict['data']['int_brief'] = ipint_list

            # define the node's ID.
            host_id = node['ip'].replace('.', '')
            if node['ip'] in router_ip_list:  # router's ID
                host_id = hostname
            self_dict['data']['id'] = host_id

            # get cdp information
            cdp_list = get_cdp(connection)
            self_dict['data']['cdp'] = cdp_list
            self_dict['data']['connections'] = len(cdp_list)

            # get vlan information
            vlan_list, vlan_class = get_vlan(connection)
            self_dict['data']['vlan'] = vlan_list
            self_dict['classes'] = ['nodes', 'switch'] + vlan_class

            connection.disconnect()
        finally:
            nodes_list.append(self_dict)
    manage_ip_list = [node['ip'] for node in nodes_dict_list] + router_ip_list

    # the node with the most connections will be the root node.
    nodes_list.sort(key=lambda x: (x['data']['connections']), reverse=True)
    while len([node for node in nodes_list if node['data']['rank'] == 0]) > 0:
        unset_rank_nodes = [node for node in nodes_list if node['data']['rank'] == 0]
        unset_rank_nodes.sort(key=lambda x: (x['data']['connections']), reverse=True)
        i = get_index('ipaddr', unset_rank_nodes[0]['data']['ipaddr'])
        nodes_list[i]['data']['rank'] = 1
        target_nodes = [node for node in unset_rank_nodes if node['data']['rank'] == 1]
        for target in target_nodes:
            print(target['data']['label'] + '  rank:' + str(target['data']['rank']))
            child_ips = [x['ipaddr'] for x in target['data']['ipaddr'] for node in unset_rank_nodes]
            for child_ip in child_ips:
                unset_rank_nodes = [node for node in nodes_list if node['data']['rank'] == 0]
                unset_rank_nodes_ip = [node['data']['ipaddr'] for node in unset_rank_nodes]
                if (child_ip in manage_ip_list) and (child_ip in unset_rank_nodes_ip):
                    i = get_index('ipaddr', child_ip)
                    target_nodes.append(nodes_list[i])
                    nodes_list[i]['data']['rank'] = target['data']['rank'] + 1
                    print(target['data']['label'] + ' -->' + nodes_list[i]['data']['label'] + '  rank:' + str(
                        nodes_list[i]['data']['rank']))

    for node in sorted(nodes_list, key=lambda x: x['data']['rank']):
        createNodesEdges(node['data']['cdp'], node['data'])
    nodes_list.sort(key=lambda x: (x['data']['label']))
    nodes_list.sort(key=lambda x: (x['data']['rank']))

    with open(output_folder + file_name, 'w') as gf:
        json.dump(nodes_list + edges_list, gf, indent=4)


if __name__ == '__main__':
    run_get_switch()
