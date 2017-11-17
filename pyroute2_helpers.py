from pyroute2 import IPRoute, IW, NetNS


def get_name(link):
    return dict(link['attrs'])['IFLA_IFNAME']


def _exclude_names(links, names):
    return [l for l in links if get_name(l) not in names]


def _exclude_kinds(links, kinds):
    result = []
    for l in links:
        attrs = dict(l['attrs'])
        try:
            info = dict(attrs['IFLA_LINKINFO']['attrs'])
            if info['IFLA_INFO_KIND'] not in kinds:
                result.append(l)
        except:
            result.append(l)
    return result


def _get_kinds(links, kinds):
    excluded = _exclude_kinds(links, kinds)
    included = []
    for link in links:
        if link not in excluded:
            included.append(link)
    return included


def get_ns_interfaces(namespace):
    with NetNS(namespace) as ns:
        return _get_kinds(ns.get_links(), ['vlan'])


def get_usable_interfaces():
    ip = IPRoute()
    iw = IW()
    wireless_interfaces = iw.get_interfaces_dict()
    links = ip.get_links()
    links = _exclude_names(links, ['lo'])
    links = _exclude_kinds(links, ['vlan'])
    wired = links
    wired = _exclude_names(wired, wireless_interfaces)
    wired = _exclude_kinds(wired, ['tun', 'bridge'])
    if len(wired):
        return [get_name(i) for i in wired]
    return [get_name(i) for i in links]

