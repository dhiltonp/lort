import re
from subprocess import TimeoutExpired, Popen, PIPE, check_call, getoutput, CalledProcessError

from netns import get_namespaces


def _request_ips(namespaces):
    # process a group of namespaces. do maybe 100 at a time to balance overhead with performance?
    procs = []
    while len([1 for ns in namespaces if ns.type is None]):
        try:
            for ns in namespaces:
                if ns.type is None:
                    check_call(f'ip netns exec {ns.ns} ip link set {ns.devices[0]} up'.split())
                    proc = Popen(
                       f'ip netns exec {ns.ns} busybox udhcpc -i {ns.devices[0]} -n -q -T 1'.split(),
                       stdout=PIPE, stderr=PIPE)
                    # switch to ip instead of busybox dhcp?
                    # proc = Popen(
                    #     f'ip netns exec {ns.ns} ip addr add 192.168.1.10/24 dev {ns.devices[0]}'.split(),
                    #     stdout=PIPE, stderr=PIPE
                    # )
                    procs.append((ns, proc))

        finally:
            for ns, proc in procs:
                try:
                    retval = proc.wait(10)  # should complete in 3s
                except TimeoutExpired:
                    ns.type = 'wan'
                else:
                    if proc.returncode == 0:
                        ns.type = 'lan'
                        lines = str(proc.stdout.read())
                        m = re.search(r'Lease of (?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) obtained, lease time', lines)
                        ns.ip = m.group('ip')
                        gateway = '.'.join(ns.ip.split('.')[:3])+'.1'
                        ns.gw = gateway
                        try:
                            check_call(f'ip netns exec {ns.ns} ip addr add {ns.ip}/24 brd + dev {ns.devices[0]}'.split())
                        except CalledProcessError as e:
                            if e.returncode != 2:  # 2==file already exists (already set up)
                                raise
                    elif proc.returncode == 1:
                        ns.type = 'wan'
                    else:
                        if proc.returncode < 0:
                            print(f'unable to discover namespace {ns.ns}, signal {-proc.returncode}')
                        else:
                            print(f'unable to discover namespace {ns.ns}, return code {proc.returncode}')
                            print('stdout:', proc.stdout.read())
                            print('stderr:', proc.stderr.read())
                proc.stdout.close()
                proc.stderr.close()

    return namespaces


def _getoutput(cmd, ns):
    return getoutput(
        f'ip netns exec {ns.ns} ssh -o StrictHostKeyChecking=no '
        f'-o UserKnownHostsFile=/dev/null root@{ns.gw} '
        f'{cmd}').strip()


def _get_cpuinfo(ns):
    cpuinfo_out = _getoutput(f'cat /proc/cpuinfo', ns)
    cpuinfo = {}
    for line in cpuinfo_out.split('\n'):
        k, v = line.split(':', 1)
        cpuinfo[k.strip()] = v.strip()
    return cpuinfo


def _get_board(ns):
    out = _getoutput('cat /tmp/sysinfo/board_name', ns)
    return out.split()[-1]


def _get_release(ns):
    out = _getoutput('cat /etc/openwrt_release', ns)
    release = {}
    for line in out.split('\n')[1:]:
        k, v = line.split('=', 1)
        release[k] = v[1:-1]
    return release


def _id_system(namespaces):
    # files:x  /proc/cpuinfo
    #          /etc/os-release
    #       x  /etc/openwrt_release
    #       x  /tmp/sysinfo/board_name
    for ns in namespaces:
        if ns.type != 'lan':
            continue
        ns.cpuinfo = _get_cpuinfo(ns)
        ns.release = _get_release(ns)
        ns.board = _get_board(ns)
    return namespaces


def discover(prefix):
    namespaces = get_namespaces(prefix)
    namespaces = _request_ips(namespaces)
    namespaces = _id_system(namespaces)

    return namespaces
