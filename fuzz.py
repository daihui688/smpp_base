from faker import Faker
import struct

import command
from utils import get_tag

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

    @property
    def random_byte(self):
        return bytes([self.random_int])

    def random_bytes(self, num):
        data = b''
        for i in range(num):
            data += self.random_byte
        return data

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

    def fuzz_bind_transceiver(self):

        # body = {
        #     'system_id': Param(type=str, max=16),
        #     'password': Param(type=str, max=9),
        #     'system_type': Param(type=str, max=13),
        #     'interface_version': Param(type=int, size=1),
        #     'addr_ton': Param(type=int, size=1),
        #     'addr_npi': Param(type=int, size=1),
        #     'address_range': Param(type=str, max=41),
        # }

        system_id = self.random_bytes(9)
        password = self.random_bytes(9)
        system_type = self.random_bytes(13)
        address_range = self.random_bytes(41)

        body = system_id + b"\x00" + password + b"\x00" + system_type + self.random_byte + \
               self.random_byte + self.random_byte + address_range
        data = self.gen_data("bind_transceiver", body)
        return data

    def fuzz_submit_sm(self):
        # params = {
        #     "command_length": None,
        #     "command_id": get_command_id(command_name),
        #     "command_status": 0,
        #     "sequence_number": self.sequence_number,
        #     "service_type": b'\x00',
        #     "source_addr_ton": random_int(),
        #     "source_addr_npi": random_int(),
        #     "source_addr": random_strs(22),
        #     "dest_addr_ton": random_int(),
        #     "dest_addr_npi": random_int(),
        #     "destination_addr": random_strs(22),
        #     "esm_class": random_int(),
        #     "protocol_id": random_int(),
        #     "priority_flag": random_int(),
        #     "schedule_delivery_time": b'\x00',
        #     "validity_period": b'\x00',
        #     "registered_delivery": random_int(),
        #     "replace_if_present_flag": random_int(),
        #     "data_coding": self.data_coding,
        #     "sm_default_msg_id": random_int(),
        #     "message_bytes": random_bytes(255)
        # }
        source_addr = self.random_bytes(21)
        destination_addr = self.random_bytes(21)
        sm_length = fake.random_int(0, 999)
        param1 = b"\x00" + self.random_bytes(2) + source_addr + b"\x00" + self.random_bytes(2) + \
                 destination_addr + b"\x00" + self.random_bytes(3) + b'\x00' + b'\x00' + \
                 self.random_bytes(3) + b"\x00"
        if sm_length < 255:
            body = param1 + struct.pack(">B", sm_length) + self.random_bytes(sm_length)
        else:
            tag = get_tag("message_payload")
            body = param1 + b'\x00' + struct.pack(">HH", tag, sm_length) + self.random_bytes(sm_length)
        data = self.gen_data("submit_sm", body)
        return data

    def fuzz_unbind(self):
        return self.gen_data("unbind")

    def fuzz_enquire_link(self):
        return self.gen_data("enquire_link")

    def fuzz_query_sm(self):
        # body = {
        #     'message_id': Param(type=str, max=65),
        #     'source_addr_ton': Param(type=int, size=1),
        #     'source_addr_npi': Param(type=int, size=1),
        #     'source_addr': Param(type=str, max=21),
        # }
        message_id = str(fake.random_int(1, 100))
        source_addr = self.random_bytes(21)
        body = message_id.encode() + b'\x00' + self.random_bytes(2) + source_addr + b'\x00'
        data = self.gen_data("query_sm", body)
        return data

    def fuzz_cancel_sm(self):
        # params = {
        #     'service_type': Param(type=str, max=6),
        #     'message_id': Param(type=str, max=65),
        #     'source_addr_ton': Param(type=int, size=1),
        #     'source_addr_npi': Param(type=int, size=1),
        #     'source_addr': Param(type=str, max=21),
        #     'dest_addr_ton': Param(type=int, size=1),
        #     'dest_addr_npi': Param(type=int, size=1),
        #     'destination_addr': Param(type=str, max=21),
        # }
        message_id = str(fake.random_int(1, 100))
        source_addr = self.random_bytes(21)
        destination_addr = self.random_bytes(21)
        body = b'\x00' + message_id.encode() + b'\x00' + self.random_bytes(2) + source_addr + b'\x00' + \
               self.random_bytes(2) + destination_addr + b'\x00'
        data = self.gen_data("cancel_sm", body)
        return data

    def fuzz_replace_sm(self):
        # body = {
        #     'message_id': Param(type=str, max=65),
        #     'source_addr_ton': Param(type=int, size=1),
        #     'source_addr_npi': Param(type=int, size=1),
        #     'source_addr': Param(type=str, max=21),
        #     'schedule_delivery_time': Param(type=int, max=17),
        #     'validity_period': Param(type=int, max=17),
        #     'registered_delivery': Param(type=int, size=1),
        #     'sm_default_msg_id': Param(type=int, size=1),
        #     'sm_length': Param(type=int, size=1),
        #     'short_message': Param(type=str, max=254, len_field='sm_length'),
        # }
        message_id = str(fake.random_int(1, 100)).encode() + b'\x00'
        source_addr = self.random_bytes(21) + b'\x00'
        sm_length = fake.random_int(0, 254)
        body = message_id + self.random_bytes(2) + source_addr + b'\x00' + b'\x00' + \
               self.random_bytes(2) + struct.pack(">B", sm_length) + self.random_bytes(sm_length)
        data = self.gen_data("replace_sm", body)
        return data

    def fuzz_deliver_sm_resp(self):
        command_id = command.get_command_id("deliver_sm_resp")
        command_status = 0
        self.sequence_number += 1
        data = struct.pack(">LLLLc", 17, command_id, command_status, self.sequence_number, b'\x00')
        return data


fuzzer = SMPPFuzz()
