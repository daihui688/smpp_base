import struct
import binascii

import sys

print(sys.byteorder)

# 打包一个整数、一个浮点数和一个字符串
data = struct.pack('if4s', 42, 3.14, b'abcd')
print(data)  # 输出：b'*\x00\x00\x00\xc3\xf5H@abcd'
print(binascii.hexlify(data))  # b'2a000000c3f5484061626364'

print(binascii.unhexlify(b'2a000000c3f5484061626364'))  # b'*\x00\x00\x00\xc3\xf5H@abcd'
# 解包字节串 data
result = struct.unpack('if4s', data)
print(result)  # 输出：(42, 3.140000104904175, b'abcd')
