import socket
import command
import consts
import struct
from faker import Faker

fake = Faker()
ascii_chars = ''.join(chr(i) for i in range(128))


def random_str():
    return fake.lexify(text="?" * fake.random_int(0, 200), letters=ascii_chars)


def random_strs(num):
    return fake.lexify(text="?" * num, letters=ascii_chars)


def random_int():
    return fake.random_int(0x00, 0xff)


def random_byte():
    return bytes([random_int()])


def random_bytes(num):
    data = b''
    for i in range(num):
        data += random_byte()
    return data


class SMPPFuzz:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        self.sequence_number = 0
        self.bind_smsc = False
        self.connect_state = False

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print("Connected to SMSC at {}:{}".format(self.host, self.port))
        except socket.error as e:
            print("Error connecting to SMSC: {}".format(e))
            self.socket = None

    def fuu_bind_transceiver(self):
        command_name = "bind_transceiver"
        command_id = command.get_command_id(command_name)
        status = consts.SMPP_ESME_ROK
        self.sequence_number += 1
        # pdu = factory(command_name)(command_id, status=consts.SMPP_ESME_ROK, sequence_number=self.sequence_number,
        #                             system_id="login", password="12345")
        # data = pdu.pack()

        system_id = random_str()
        password = random_str()

        body = system_id.encode() + b"\x00" + password.encode() + b"\x00" + b"\x00" + random_byte() + random_byte() + random_byte() + b"\x00"
        header = struct.pack(">LLLL", 16 + len(body), command_id, status, self.sequence_number)
        data = header + body
        print(data)
        self.socket.sendall(data)

    def fuu_submit_sm(self):
        command_name = "submit_sm"
        command_id = command.get_command_id(command_name)
        status = consts.SMPP_ESME_ROK
        self.sequence_number += 1
        source_addr = fake.ipv4()
        destination_addr = fake.ipv4()
        message = random_str()
        # f">LLLL3s{len(self.source_addr) + 1}sH{len(self.destination_addr) + 1}sL3sBBB{len(self.message)}s")
        body = random_bytes(3) + source_addr.encode() + b"\x00" + random_bytes(
            2) + destination_addr.encode() + b"\x00" + random_bytes(7) + random_bytes(2) + struct.pack("B",
                                                                                                       len(message)) + random_str().encode()
        header = struct.pack(">LLLL", 16 + len(body), command_id, status, self.sequence_number)
        data = header + body
        print(data)
        self.socket.sendall(data)


if __name__ == "__main__":
    print(ascii_chars)
