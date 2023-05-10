import logging
import socket
import struct
import threading
import time

import config
import consts
from command import get_command_id, get_command_name
from fuzz import random_str, random_bytes, static_str
from pdu import get_pdu
from utils import get_optional_param_name, contains_chinese


class SMPPClient:
    def __init__(self, host):
        self.host = host
        self.client = None
        self.sequence_number = 0
        self.client_state = consts.SMPP_CLIENT_STATE_CLOSED
        self.data_coding = consts.SMPP_ENCODING_DEFAULT
        self.last_message_id = None

        # Set up logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def connect(self, host, port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 客户端绑定到self.host,0表示让系统自动选择一个可用的空闲端口
        self.client.bind((self.host, 0))
        self.client.connect((host, port))
        self.client_state = consts.SMPP_CLIENT_STATE_OPEN
        self.logger.info(f"{self.client.getsockname()}连接到SMSC{host}:{port}")
        t1 = threading.Thread(target=self.handle)
        t1.start()
        self.bind_transceiver()
        time.sleep(0.1)

    def disconnect(self):
        if self.client:
            self.logger.warning(f"ESME{self.client.getsockname()}断开连接")
            self.client.close()
            self.client_state = consts.SMPP_CLIENT_STATE_CLOSED
            self.client = None

    def run(self, count, loop, interval):
        """
        :param count: 发送数量
        :param loop: 循环次数
        :param interval: 发送间隔
        """
        t2 = threading.Thread(target=self.enquire)
        t2.start()
        if 2 <= self.client_state <= 4:
            option = eval(input("请输入你要执行的操作编号(0.测试,1.发送消息,2.模糊测试):"))
            if option == 0:
                self.query_sm(self.last_message_id)
                self.cancel_sm(self.last_message_id)
                self.replace_sm(self.last_message_id, "daihui666")
            elif option == 1:
                for i in range(count):
                    msg = input("请输入消息(输入q退出):")
                    if contains_chinese(msg):
                        self.data_coding = consts.SMPP_ENCODING_ISO10646
                    if self.client_state in (consts.SMPP_CLIENT_STATE_BOUND_TX, consts.SMPP_CLIENT_STATE_BOUND_TRX):
                        if msg.strip().upper() == "Q":
                            self.unbind()
                            break
                        self.submit_sm(msg)
                        # self.data_sm(msg)
                        time.sleep(interval)
            elif option == 2:
                for i in range(loop):
                    self.logger.info(f"Starting fuzz {fuzz_num}")
                    self.fuzz_submit_sm(count, interval)
            else:
                self.logger.error("错误的编号!")
        else:
            self.logger.error("绑定失败!")

    def handle(self):
        while True:
            if not self.client:
                break
            length = self.client.recv(4)
            command_length = struct.unpack(">L", length)[0]
            resp = length + self.client.recv(command_length - 4)
            command_id = struct.unpack(">L", resp[4:8])[0]
            command_name = get_command_name(command_id)
            if command_name == "bind_transceiver_resp":
                self.parse_bind_transceiver_resp(resp, command_name)
            elif command_name == "submit_sm_resp":
                self.parse_submit_sm_resp(resp, command_name)
            elif command_name == "deliver_sm":
                self.parse_deliver_sm(resp, command_name)
            elif command_name == "data_sm_resp":
                self.parse_data_sm_resp(resp, command_name)
            elif command_name == "query_sm_resp":
                self.parse_query_sm_resp(resp, command_name)
            elif command_name == "enquire_link_resp":
                self.parse_enquire_link_resp(resp, command_name)
            elif command_name == "cancel_sm_resp":
                self.parse_cancel_sm_resp(resp, command_name)
            elif command_name == "replace_sm_resp":
                self.parse_replace_sm_resp(resp, command_name)
            elif command_name == "unbind_resp":
                self.parse_unbind_resp(resp, command_name)
            elif command_name == "generic_nack":
                self.parse_generic_nack(resp, command_name)
            elif command_name == "alert_notification":
                self.parse_alert_notification(resp)
            else:
                self.logger.error("异常数据")

    def enquire(self):
        while True:
            if self.client is None:
                break
            try:
                self.enquire_link()
                time.sleep(30)
            except AttributeError as e:
                self.logger.error(e)

    @staticmethod
    def parse_base_resp(resp, command_name):
        pdu = get_pdu(command_name)()
        resp_data = pdu.unpack(resp)
        pdu.command_length, pdu.command_id, pdu.command_status, pdu.sequence_number = resp_data
        return pdu

    def base_send_sm(self, command_name, **kwargs):
        command_id = get_command_id(command_name)
        self.sequence_number += 1
        pdu = get_pdu(command_name)(command_id, command_status=0, sequence_number=self.sequence_number, **kwargs)
        data = pdu.pack()
        self.client.sendall(data)

    def bind_transceiver(self):
        self.base_send_sm("bind_transceiver", system_id=config.SYSTEM_ID, password=config.PASSWORD)

    def parse_bind_transceiver_resp(self, resp, command_name):
        system_id = resp[16:-1]
        pdu = get_pdu(command_name)(system_id=system_id)
        resp_data = pdu.unpack(resp)
        pdu.command_length, pdu.command_id, pdu.command_status, pdu.sequence_number, pdu.system_id, _ = resp_data

        if pdu.sequence_number == self.sequence_number and pdu.command_status == consts.SMPP_ESME_ROK:
            self.logger.info(f"与SMSC绑定成功,{pdu}")
            self.client_state = consts.STATE_SETTERS[command_name]

    def submit_sm(self, message):
        self.base_send_sm("submit_sm", source_addr=config.SOURCE_ADDR, destination_addr=config.DESTINATION_ADDR,
                          data_coding=self.data_coding, message=message)

    def parse_submit_sm_resp(self, resp, command_name):
        message_id = resp[16:-1]
        pdu = get_pdu(command_name)(message_id=message_id)
        resp_data = pdu.unpack(resp)
        pdu.command_length, pdu.command_id, pdu.command_status, pdu.sequence_number, pdu.message_id = resp_data[:-1]
        if pdu.sequence_number == self.sequence_number and pdu.command_status == consts.SMPP_ESME_ROK:
            self.logger.info(f"发送消息成功,{pdu}")
            self.last_message_id = pdu.message_id.decode()

    def data_sm(self, message):
        self.base_send_sm("data_sm", source_addr=config.SOURCE_ADDR, destination_addr=config.DESTINATION_ADDR,
                          data_coding=self.data_coding, message=message)

    def parse_data_sm_resp(self, resp, command_name):
        message_id = resp[16:-1]
        pdu = get_pdu(command_name)(message_id=message_id)
        resp_data = pdu.unpack(resp)
        pdu.command_length, pdu.command_id, pdu.command_status, pdu.sequence_number, pdu.message_id = resp_data[:-1]

        if pdu.sequence_number == self.sequence_number and pdu.command_status == consts.SMPP_ESME_ROK:
            self.logger.info(f"发送消息成功,{pdu}")

    def parse_deliver_sm(self, resp, command_name):
        sm_length = resp[56]
        short_message = resp[57:57 + sm_length]
        optional_params = resp[57 + sm_length:]
        # print(sm_length)
        # print(short_message)
        # print(optional_params)
        pdu = get_pdu(command_name)(source_addr=config.SOURCE_ADDR, destination_addr=config.DESTINATION_ADDR,
                                    sm_length=sm_length, optional_params=optional_params)
        resp_data = pdu.unpack(resp)
        pdu.command_length, pdu.command_id, pdu.command_status, pdu.sequence_number = resp_data[:4]
        pdu.optional_params = resp_data[-1]
        if sm_length != 0:
            pdu.short_message = resp_data[-2]
        else:
            pdu.optional_params = resp_data[-1]
            optional_param_type = struct.unpack(">H", pdu.optional_params[:2])[0]
            optional_param_name = get_optional_param_name(optional_param_type)
            # print(optional_param_name)
            optional_param_length = struct.unpack(">H", pdu.optional_params[2:4])[0]
            # print(optional_param_length)
            payload = pdu.optional_params[4:4 + optional_param_length]
            data = payload[94:-9]
            print(data.decode())
        if pdu.command_status == consts.SMPP_ESME_ROK:
            self.deliver_sm_resp(pdu.sequence_number)

    def deliver_sm_resp(self, sequence_number):
        self.base_send_sm("deliver_sm_resp")

    def query_sm(self, message_id):
        self.base_send_sm("query_sm", source_addr=config.SOURCE_ADDR, message_id=message_id)

    def parse_query_sm_resp(self, resp, command_name):
        message_id = resp[16:-3]
        pdu = get_pdu(command_name)(message_id=message_id)
        resp_data = pdu.unpack(resp)
        pdu.command_length, pdu.command_id, pdu.command_status, pdu.sequence_number, pdu.message_id, pdu.final_date, \
            pdu.message_state, pdu.error_code = resp_data
        if pdu.sequence_number == self.sequence_number:
            self.logger.info(f"消息状态:{pdu}")

    def cancel_sm(self, message_id):
        self.base_send_sm("cancel_sm", message_id=message_id, source_addr=config.SOURCE_ADDR,
                          destination_addr=config.DESTINATION_ADDR)

    def parse_cancel_sm_resp(self, resp, command_name):
        pdu = self.parse_base_resp(resp, command_name)
        if pdu.sequence_number == self.sequence_number:
            print(command_name, pdu)

    def replace_sm(self, message_id, new_message):
        self.base_send_sm("replace_sm", message_id=message_id, source_addr=config.SOURCE_ADDR, new_message=new_message,
                          data_coding=self.data_coding)

    def parse_replace_sm_resp(self, resp, command_name):
        pdu = self.parse_base_resp(resp, command_name)
        if pdu.sequence_number == self.sequence_number:
            print(command_name, pdu)

    def unbind(self):
        self.base_send_sm("unbind")

    def parse_unbind_resp(self, resp, command_name):
        pdu = self.parse_base_resp(resp, command_name)
        if pdu.sequence_number == self.sequence_number and pdu.command_status == consts.SMPP_ESME_ROK:
            print("解绑成功,", pdu)
            self.client_state = consts.STATE_SETTERS[command_name]
            self.disconnect()

    def enquire_link(self):
        self.base_send_sm("enquire_link")

    def parse_enquire_link_resp(self, resp, command_name):
        pdu = self.parse_base_resp(resp, command_name)
        if pdu.sequence_number == self.sequence_number and pdu.command_status == consts.SMPP_ESME_ROK:
            pass
        else:
            self.client_state = consts.SMPP_CLIENT_STATE_OPEN

    def parse_generic_nack(self, resp, command_name):
        pdu = self.parse_base_resp(resp, command_name)
        if pdu.sequence_number == self.sequence_number:
            print(command_name, pdu)

    def parse_alert_notification(self, resp):
        sm_length = resp[56]
        short_message = resp[57:57 + sm_length]
        optional_params = resp[57 + sm_length:]
        # print(sm_length)
        # print(short_message)
        # print(optional_params)
        pdu = get_pdu("deliver_sm")(source_addr=config.SOURCE_ADDR, esme_addr=config.ESME_ADDR, sm_length=sm_length,
                                    optional_params=optional_params)
        resp_data = pdu.unpack(resp)
        pdu.command_length, pdu.command_id, pdu.command_status, pdu.sequence_number = resp_data[:4]
        pdu.optional_params = resp_data[-1]
        if sm_length != 0:
            pdu.short_message = resp_data[-2]
        else:
            pdu.optional_params = resp_data[-1]
            optional_param_type = struct.unpack(">H", pdu.optional_params[:2])[0]
            optional_param_name = get_optional_param_name(optional_param_type)
            # print(optional_param_name)
            optional_param_length = struct.unpack(">H", pdu.optional_params[2:4])[0]
            # print(optional_param_length)
            payload = pdu.optional_params[4:4 + optional_param_length]
            data = payload[94:-9]
            print(data.decode())
        if pdu.command_status == consts.SMPP_ESME_ROK:
            self.deliver_sm_resp(pdu.sequence_number)

    def fuzz_submit_sm(self, _count, _interval):
        global fuzz_num
        for _ in range(_count):
            command_name = "submit_sm"
            command_id = get_command_id(command_name)
            command_status = consts.SMPP_ESME_ROK
            self.sequence_number += 1
            source_addr = static_str(22)
            destination_addr = static_str(22)
            message = static_str(161)
            body = random_bytes(3) + source_addr.encode() + b"\x00" + random_bytes(
                2) + destination_addr.encode() + b"\x00" + random_bytes(7) + random_bytes(2) + struct.pack("B",
                                                                                                           len(message)) + random_str().encode()
            header = struct.pack(">LLLL", 16 + len(body), command_id, command_status, self.sequence_number)
            data = header + body
            print(data)
            try:
                self.client.sendall(data)
                self.logger.info(f"Fuzz {fuzz_num} completed successfully")
            except BrokenPipeError as e:
                self.connect(config.SMPP_SERVER_HOST, config.SMPP_SERVER_PORT)
                self.client.sendall(data)
                self.logger.warning(f"Fuzz {fuzz_num} BrokenPipeError: {e}")
            except Exception as e:
                self.logger.error(f"Fuzz {fuzz_num} failed with error: {e}")
            finally:
                fuzz_num += 1
                time.sleep(_interval)
