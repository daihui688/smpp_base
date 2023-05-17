import argparse


import config
from client import SMPPClient
from utils import get_interfaces_and_ips


def parse_terminal_params():
    parser = argparse.ArgumentParser(description="smpp协议参数")
    parser.add_argument("-i", "--interface", default="lo", type=str, help="网络接口")
    parser.add_argument("-c", "--count", default=100, type=int, help="发送数量")
    parser.add_argument("-l", "--loop", default=1, type=int, help="循环次数")
    parser.add_argument("-t", "--interval", default=0, type=float, help="间隔时间")

    args = parser.parse_args()
    print(args)
    return args.interface, args.count, args.loop, args.interval


if __name__ == '__main__':
    interface, count, loop, interval = parse_terminal_params()
    interfaces_ips = get_interfaces_and_ips()
    host = interfaces_ips.get(interface)
    client = SMPPClient(host)
    client.connect()
    client.fuzz(count, loop, interval)
