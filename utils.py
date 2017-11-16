from itertools import chain

from pyroute2 import IPRoute, IW


def get_name(link):
    return dict(link['attrs'])['IFLA_IFNAME']


def _exclude_name(links, value):
    return [l for l in links if value != get_name(l)]


def _exclude_kind(links, value):
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


def get_usable_interfaces():
    ip = IPRoute()
    iw = IW()
    wireless_interfaces = iw.get_interfaces_dict()
    links = ip.get_links()
    tmp = links
    for name in chain(wireless_interfaces, ['lo']):
        tmp = _exclude_name(tmp, name)
    for kind in ['vlan', 'tun', 'bridge']:
        tmp = _exclude_kind(tmp, kind)

    return [get_name(i) for i in tmp]
