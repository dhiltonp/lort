#!/usr/bin/python3
import argparse
from itertools import chain
from subprocess import check_call, getoutput

from pyroute2 import IPRoute, IW, NetNS


def setup_netns(device, prefix, vlan):
    vlan_dev = f'{device[:5]}_{vlan}'
    namespace = f'{prefix}_{vlan}'
    check_call(f'ip netns add {namespace}'.split(' '))
    check_call(f'ip link add link {device} name {vlan_dev} type vlan id {vlan}'.split(' '))
    check_call(f'ip link set {vlan_dev} netns {namespace}'.split(' '))
    check_call(f'ip netns exec {namespace} ifconfig {vlan_dev} 192.168.0.{vlan}/24 up'.split(' '))


def teardown_netns(prefix, vlan):
    namespace = f'{prefix}_{vlan}'
    check_call(f'ip netns del {namespace}'.split(' '))


def get_netns_vlans(prefix):
    unfiltered = getoutput('ip netns list').split('\n')
    filtered = [ns for ns in unfiltered if ns.startswith(prefix)]
    ids = [int(ns[len(prefix) + 1:]) for ns in filtered]
    return sorted(ids)


def list_netns(prefix):
    final = [f'{prefix}_{id}' for id in get_netns_vlans(prefix)]
    return final


def vlans_parser(string):
    vlans = []
    for part in string.split(','):
        vrange = part.split('-')
        if len(vrange) == 1:
            vlans.append(int(vrange[0]))
        elif len(vrange) == 2:
            start = int(vrange[0])
            end = int(vrange[1])
            vlans.extend(range(start, end+1))

    vlans = list(set(vlans))
    vlans = sorted(vlans)

    return sorted(vlans)


def validate_vlan_range(vlans):
    errors = []
    if vlans[0] < 2:
        errors.append(f'lowest vlan ({vlans[0]}) < 2')
    if vlans[-1] > 250:
        errors.append(f'highest vlan ({vlans[-1]}) > 250')

    return errors


def get_name(link):
    return dict(link['attrs'])['IFLA_IFNAME']


def exclude_name(links, value):
    return [l for l in links if value != get_name(l)]


def exclude_kind(links, value):
    result = []
    for l in links:
        attrs = dict(l['attrs'])
        try:
            info = dict(attrs['IFLA_LINKINFO']['attrs'])
            if info['IFLA_INFO_KIND'] != value:
                result.append(l)
        except:
            result.append(l)
    return result


def get_interfaces():
    ip = IPRoute()
    iw = IW()
    wireless_interfaces = iw.get_interfaces_dict()
    links = ip.get_links()
    tmp = links
    for name in chain(wireless_interfaces, ['lo']):
        tmp = exclude_name(tmp, name)
    for kind in ['vlan', 'tun', 'bridge']:
        tmp = exclude_kind(tmp, kind)

    return tmp


def parse_args():
    parser = argparse.ArgumentParser(description='setup namespaces for network testing, one per vlan')
    parser.add_argument('--prefix', help='network namespace prefix', default='wrt_test')
    subparsers = parser.add_subparsers(help='help for subcommand', dest='command')

    setup_parser = subparsers.add_parser('setup')
    setup_parser.add_argument('device',
                              help='network device to operate on',
                              choices=[get_name(i) for i in get_interfaces()])
    setup_parser.add_argument('vlans', type=vlans_parser,
                              help='vlans to work on ("2", "2-10", "2-10,20-30")')

    teardown_parser = subparsers.add_parser('teardown')
    teardown_parser.add_argument('vlans',
                                 type=vlans_parser,
                                 help='vlans to work on ("2", "2-10", "2-10,20-30")')

    discover_parser = subparsers.add_parser('discover')

    list_parser = subparsers.add_parser('list')

    args = parser.parse_args()
    if args.command is None:
        parser.print_usage()
        exit(2)
    if args.command in ['setup', 'teardown']:
        errors = validate_vlan_range(args.vlans)
        if errors:
            [print(e) for e in errors]
            exit(1)

    return args


if __name__ == '__main__':
    args = parse_args()
    if args.command == 'setup':
        current_vlans = get_netns_vlans(args.prefix)
        for vlan in args.vlans:
            if vlan not in current_vlans:
                setup_netns(args.device, args.prefix, vlan)
    elif args.command == 'teardown':
        current_vlans = get_netns_vlans(args.prefix)
        for vlan in args.vlans:
            if vlan in current_vlans:
                teardown_netns(args.prefix, vlan)
    elif args.command == 'list':
        out = list_netns(args.prefix)
        [print(ns) for ns in out]
    elif args.command == 'discover':
        raise NotImplementedError
