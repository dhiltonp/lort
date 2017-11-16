from subprocess import check_call, getoutput


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