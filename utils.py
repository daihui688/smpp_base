import netifaces

import consts

interfaces_ips = {}


def get_interfaces_and_ips():
    for iface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(iface)
        if netifaces.AF_INET in addrs:
            ip_address = addrs[netifaces.AF_INET][0]['addr']
            interfaces_ips[iface] = ip_address
    return interfaces_ips


def get_optional_param_name(num):
    for name, v in consts.OPTIONAL_PARAMS.items():
        if v == num:
            return name


def get_tag(name):
    return consts.OPTIONAL_PARAMS.get(name)


def contains_chinese(message):
    for char in message:
        if '\u4e00' <= char <= '\u9fff':
            return True
    return False
