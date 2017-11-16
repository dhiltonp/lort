#!/usr/bin/python3
import argparse

from netns import setup_netns, teardown_netns, get_netns_vlans, list_netns
from utils import get_usable_interfaces


def vlans_parser(string):
    """
    converts a string describing a numeric range ('10', '10-15',
    '10-15,20-25'), and returns a list of all values.
    """
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


def parse_args():
    parser = argparse.ArgumentParser(description='setup namespaces for network testing, one per vlan')
    parser.add_argument('--prefix', help='network namespace prefix', default='wrt_test')
    subparsers = parser.add_subparsers(help='help for subcommand', dest='command')

    setup_parser = subparsers.add_parser('setup')
    setup_parser.add_argument('device',
                              help='network device to operate on',
                              choices=get_usable_interfaces())
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
