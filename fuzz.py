from faker import Faker
import struct

import command
import consts
from utils import get_pdu

fake = Faker()
ascii_chars = ''.join(chr(i) for i in range(128))


class SMPPFuzz:
    def __init__(self):
        self.sequence_number = 0

    @property
    def random_char(self):
        return fake.lexify(text="?", letters=ascii_chars)

    @property
    def random_str(self):
        return fake.lexify(text="?" * fake.random_int(0, 200), letters=ascii_chars)

    @staticmethod
    def random_strs(num):
        return fake.lexify(text="?" * num, letters=ascii_chars)

    @property
    def random_int(self):
        return fake.random_int(0x00, 0xff)

    @staticmethod
    def random_ints(num):
        return fake.random_int(0xff * (num - 1), 0xff * num)

    @property
    def random_byte(self):
        return bytes([self.random_int])

    def random_bytes(self, num):
        data = b''
        for i in range(num):
            data += self.random_byte
        return data
    def gen_body(self,command_name):
        body = b''
        pdu = get_pdu(command_name)
        try :
            pdu.body
        except AttributeError:
            return body
        for k, v in pdu.body.items():
            param = b''
            size = v.size
            if v.type == str:
                if not v.size:
                    size = self.random_int
                    if v.max:
                        size = v.max
                param = struct.pack(f">{size}s", self.random_strs(size).encode())
            elif v.type == int:
                c = consts.INT_PACK_FORMATS.get(v.size)
                param = struct.pack(">" + c, self.random_ints(v.size))
            body += param
        return body
    def gen_data(self, command_name, body=None):
        command_id = command.get_command_id(command_name)
        command_status = 0
        self.sequence_number += 1
        if body is None:
            header = struct.pack(">LLLL", 16, command_id, command_status, self.sequence_number)
            return header
        else:
            command_length = 16 + len(body)
            header = struct.pack(">LLLL", command_length, command_id, command_status, self.sequence_number)
            data = header + body
            return data
    def fuzz_data(self,command_name):
        body = self.gen_body(command_name)
        data = self.gen_data(command_name, body)
        return data



fuzzer = SMPPFuzz()
