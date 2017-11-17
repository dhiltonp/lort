from subprocess import check_call, getoutput, run

from pyroute2_helpers import get_name, get_ns_interfaces


def setup_netns(device, prefix, vlan):
    vlan_dev = f'{device[:5]}_{vlan}'
    namespace = f'{prefix}_{vlan}'
    check_call(f'ip netns add {namespace}'.split())
    check_call(f'ip link add link {device} name {vlan_dev} type vlan id {vlan}'.split())
    check_call(f'ip link set {vlan_dev} netns {namespace}'.split())
#    check_call(f'ip netns exec {namespace} ifconfig {vlan_dev} 192.168.0.{vlan}/24 up'.split())
    #check_call(f'ip netns exec {namespace} ip addr add 192.168.0.{vlan}/24 brd + dev {vlan_dev}'.split())


def exec_netns(namespace, cmd):
    args = f'ip netns exec {namespace}'.split()
    args.extend(cmd)
    proc = run(args)
    return proc


def teardown_netns(namespace, devices):
    for dev in devices:
        run(f'ip netns exec {namespace} ip link del {dev}', shell=True)
    check_call(f'ip netns del {namespace}'.split())


def get_namespaces(prefix):
    namespaces = getoutput('ip netns list').split('\n')
    filtered = [ns for ns in namespaces if ns.startswith(prefix)]
    results = {}
    for ns in filtered:
        results[ns] = [get_name(ns) for ns in get_ns_interfaces(ns)]
    return results

