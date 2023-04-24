import socket
import threading
import time
from pdu import *


class SMPPClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        self.sequence_number = 0
        self.bind_smsc = False
        self.connect_state = False

    @staticmethod
    def contains_chinese(message):
        for char in message:
            if '\u4e00' <= char <= '\u9fff':
                return True
        return False

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print("Connected to SMSC at {}:{}".format(self.host, self.port))
            self.start()
        except socket.error as e:
            print("Error connecting to SMSC: {}".format(e))
            self.socket = None

    def start(self):
        self.bind_transceiver()
        self.parse_bind_transceiver_resp()
        if self.bind_smsc:
            while True:
                msg = input("请输入你要发送的消息:")
                if msg.upper() == "Q":
                    client.unbind()
                    client.parse_unbind_resp()
                    return
                if self.connect_state:
                    self.submit_sm(msg)
                    self.parse_submit_sm_resp()

    def enquire(self):
        t = threading.Thread(target=self.enquires())
        t.setDaemon(True)
        t.start()

    def enquires(self):
        try:
            self.enquire_link()
            self.enquire_link_resp()
            time.sleep(5)
        except AttributeError as e:
            pass

    def disconnect(self):
        if self.socket:
            self.socket.close()
            self.socket = None
            print("Disconnected from SMSC")

    def bind_transceiver(self):
        command_name = "bind_transceiver"
        command_id = command_types.get_command_code(command_name)
        self.sequence_number += 1
        pdu = factory(command_name)(command_id, result=consts.SMPP_ESME_ROK, sequence_number=self.sequence_number,
                                    system_id="login", password="12345")
        data = pdu.pack()
        # print(data)
        self.socket.sendall(data)

    def parse_bind_transceiver_resp(self):
        reply = self.socket.recv(1024)
        # print(reply)
        system_id = reply[16:-1]
        # print(system_id)
        pdu = factory("bind_transceiver_resp")(system_id=system_id)
        resp_data = pdu.unpack(reply)
        print(resp_data)
        pdu.length, pdu.command_id, pdu.result, pdu.sequence_number, pdu.system_id, _ = resp_data

        if pdu.sequence_number == self.sequence_number and pdu.result == consts.SMPP_ESME_ROK:
            print("绑定成功,", pdu)
            self.bind_smsc = True
            self.connect_state = True

    def submit_sm(self, message):
        command_name = "submit_sm"
        command_id = command_types.get_command_code(command_name)
        data_coding = consts.SMPP_ENCODING_DEFAULT
        if self.contains_chinese(message):
            data_coding = consts.SMPP_ENCODING_ISO10646

        # def __init__(self, command_id, sequence_number, result, source_addr, destination_addr, data_coding,
        #                  message):
        self.sequence_number += 1
        pdu = factory(command_name)(command_id, result=consts.SMPP_ESME_ROK, sequence_number=self.sequence_number,
                                    source_addr="MySMSSClient",
                                    destination_addr="MySMSService", data_coding=data_coding, message=message)
        data = pdu.pack()
        # print(data)
        self.socket.sendall(data)

    def parse_submit_sm_resp(self):
        resp = self.socket.recv(1024)
        # print(resp)
        message_id = resp[16:-1]
        # print(message_id,len(message_id))
        pdu = factory("submit_sm_resp")(message_id=message_id)
        resp_data = pdu.unpack(resp)
        print(resp_data)
        pdu.length, pdu.command_id, pdu.result, pdu.sequence_number, pdu.message_id, _ = resp_data

        if pdu.sequence_number == self.sequence_number and pdu.result == consts.SMPP_ESME_ROK:
            print("发送消息成功,", pdu)
            self.parse_deliver_sm()

    def parse_deliver_sm(self, resp=None):
        if resp is None:
            resp = self.socket.recv(1024)
        # print(resp)
        source_addr = "MySMSService"
        destination_addr = "MySMSSClient"
        message = resp[57:]
        # print("message:",message)
        pdu = factory("deliver_sm")(source_addr=source_addr, destination_addr=destination_addr, message=message)
        resp_data = pdu.unpack(resp)
        print(resp_data)
        pdu.length, pdu.command_id, pdu.result, pdu.sequence_number, _, pdu.source_addr, _, pdu.destination_addr, _, _, _, _, _, pdu.message = resp_data

        if pdu.result == consts.SMPP_ESME_ROK:
            print(f"收到消息:{pdu.message}")
            # print(pdu)
            self.deliver_sm_resp(pdu.sequence_number)

    def deliver_sm_resp(self, sequence_number):
        command_name = "deliver_sm_resp"
        command_id = command_types.get_command_code(command_name)
        self.sequence_number = sequence_number
        pdu = factory(command_name)(command_id, result=consts.SMPP_ESME_ROK, sequence_number=self.sequence_number)
        data = pdu.pack()
        # print(data)
        self.socket.sendall(data)

    def unbind(self):
        command_name = "unbind"
        command_id = command_types.get_command_code(command_name)
        self.sequence_number += 1
        pdu = factory(command_name)(command_id, result=consts.SMPP_ESME_ROK, sequence_number=self.sequence_number)
        data = pdu.pack()
        # print(data)
        self.socket.sendall(data)

    def parse_unbind_resp(self):
        resp = self.socket.recv(1024)
        # print(resp)
        pdu = factory("unbind_resp")()
        resp_data = pdu.unpack(resp)
        print(resp_data)
        pdu.length, pdu.command_id, pdu.result, pdu.sequence_number = resp_data

        if pdu.sequence_number == self.sequence_number and pdu.result == consts.SMPP_ESME_ROK:
            print("解绑成功,", pdu)
            self.disconnect()

    def enquire_link(self):
        command_name = "enquire_link"
        command_id = command_types.get_command_code(command_name)
        pdu = factory(command_name)(command_id, result=consts.SMPP_ESME_ROK, sequence_number=self.sequence_number)
        data = pdu.pack()
        # print(data)
        self.socket.sendall(data)

    def enquire_link_resp(self):
        resp = self.socket.recv(1024)
        # print(resp)
        pdu = factory("enquire_link_resp")()
        resp_data = pdu.unpack(resp)
        print(resp_data)
        pdu.length, pdu.command_id, pdu.result, pdu.sequence_number = resp_data

        if pdu.sequence_number == self.sequence_number and pdu.result == consts.SMPP_ESME_ROK:
            print("连接成功,", pdu)
            self.connect_state = True
        else:
            self.connect_state = False


host = "localhost"
port = 7777

client = SMPPClient(host, port)
client.connect()
client.enquire()
