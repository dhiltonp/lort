from collections import defaultdict
from subprocess import check_call, getoutput, run

from pyroute2_helpers import get_name, get_ns_interfaces


class NSInfo:
    def __init__(self, ns):
        self.ns = ns
        self.devices = {}
        self.type = None
        self.cpuinfo = defaultdict(str)
        self.release = defaultdict(str)
        self.board = None

    def __str__(self):
        return f'{self.ns}\t{self.release["DISTRIB_REVISION"]}\t{self.board}\t{self.cpuinfo["machine"]}'

def setup_netns(device, prefix, vlan):
    vlan_dev = f'{device[:5]}_{vlan}'
    namespace = f'{prefix}_{vlan}'
    check_call(f'ip netns add {namespace}'.split())
    check_call(f'ip link add link {device} name {vlan_dev} type vlan id {vlan}'.split())
    check_call(f'ip link set {vlan_dev} netns {namespace}'.split())
#    check_call(f'ip netns exec {namespace} ifconfig {vlan_dev} 192.168.0.{vlan}/24 up'.split())
    #check_call(f'ip netns exec {namespace} ip addr add 192.168.0.{vlan}/24 brd + dev {vlan_dev}'.split())


def exec_netns(namespace, cmd, timeout=None):
    args = f'ip netns exec {namespace}'.split()
    args.extend(cmd)
    proc = run(args, timeout=timeout)
    return proc


def teardown_netns(namespace, devices):
    for dev in devices:
        check_call(f'ip netns exec {namespace} ip link del {dev}', shell=True)
    check_call(f'ip netns del {namespace}'.split())


def get_namespaces(prefix):
    namespaces = getoutput('ip netns list').split('\n')
    filtered = [ns for ns in namespaces if ns.startswith(prefix)]
    results = []
    for ns in filtered:
        info = NSInfo(ns)
        info.devices = [get_name(ns) for ns in get_ns_interfaces(ns)]
        results.append(info)

    # results = {}
    # for ns in filtered:
    #     results[ns] = [get_name(ns) for ns in get_ns_interfaces(ns)]
    return results

