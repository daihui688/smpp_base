import logging
import socket
import struct
import threading
import time

import config
import consts
from command import get_command_id, get_command_name
from fuzz import fuzzer
from pdu import get_pdu
from utils import contains_chinese


class SMPPClient:
    def __init__(self, host):
        self.host = host
        self.client = None
        self.sequence_number = 0
        self.client_state = consts.SMPP_CLIENT_STATE_CLOSED
        self.data_coding = consts.SMPP_ENCODING_DEFAULT
        self.last_message_id = None
        self.fuzz_num = 0

        # Set up logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def connect(self, host="127.0.0.1", port_pool=(7777, 7778)):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 客户端绑定到self.host,0表示让系统自动选择一个可用的空闲端口
        self.client.bind((self.host, 0))
        for port in port_pool:
            try:
                self.client.connect((host, port))
            except Exception as e:
                self.logger.error(f"连接到SMSC{host}:{port}失败,{e}")
                if port == port_pool[-1]:
                    self.logger.error("无可用SMSC服务器！")
                continue
            else:
                self.logger.info(f"{self.client.getsockname()}连接到SMSC{host}:{port}")
                break
        self.client_state = consts.SMPP_CLIENT_STATE_OPEN
        t1 = threading.Thread(target=self.handle)
        t1.start()

    def bind(self):
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
        self.bind()
        t2 = threading.Thread(target=self.enquire)
        t2.start()
        if 2 <= self.client_state <= 4:
            while True:
                option = input("请输入你要执行的操作编号(0.测试,1.发送消息):")
                if option == "0":
                    self.query_sm(self.last_message_id)
                    time.sleep(interval)
                    self.cancel_sm(self.last_message_id)
                    time.sleep(interval)
                    self.replace_sm(self.last_message_id, "daihui666")
                elif option == "1":
                    for i in range(count):
                        msg = input("请输入消息(输入q退出):")
                        if contains_chinese(msg):
                            self.data_coding = consts.SMPP_ENCODING_ISO10646
                        if msg.strip().upper() == "Q":
                            break
                        self.submit_sm(msg)
                        # self.data_sm(msg)
                        time.sleep(interval)
                elif option == "q":
                    self.unbind()
                    break
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
                with open(f"./data/err_resp_data/{self.fuzz_num}", "wb") as f:
                    f.write(resp)

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
        header = {
            "command_length": None,
            "command_id": None,
            "command_status": None,
            "sequence_number": None
        }
        pdu = get_pdu(command_name)(**header)
        resp_data = pdu.unpack(resp)
        pdu.command_length, pdu.command_id, pdu.command_status, pdu.sequence_number = resp_data
        return pdu

    def base_send_sm(self, command_name, **kwargs):
        command_id = get_command_id(command_name)
        self.sequence_number += 1
        pdu = get_pdu(command_name)(command_id=command_id, command_status=0, sequence_number=self.sequence_number,
                                    **kwargs)
        data = pdu.pack()
        self.client.sendall(data)
        return data

    def bind_transceiver(self):
        body = {
            'system_id': config.SYSTEM_ID,
            'password': config.PASSWORD,
            'system_type': "sms",
            'interface_version': consts.SMPP_VERSION_34,
            'addr_ton': consts.SMPP_TON_INTL,
            'addr_npi': consts.SMPP_NPI_ISDN,
            'address_range': consts.NULL_BYTE,
        }
        self.base_send_sm("bind_transceiver", **body)

    def parse_bind_transceiver_resp(self, resp, command_name):
        system_id = resp[16:-1]
        pdu = get_pdu(command_name)(system_id=system_id)
        resp_data = pdu.unpack(resp)
        pdu.command_length, pdu.command_id, pdu.command_status, pdu.sequence_number, pdu.system_id = resp_data[:-1]
        if pdu.sequence_number == self.sequence_number and pdu.command_status == consts.SMPP_ESME_ROK:
            self.logger.info(f"与SMSC绑定成功,{pdu}")
            self.client_state = consts.STATE_SETTERS[command_name]

    def submit_sm(self, message):
        body = {
            "service_type": "CMT",
            "source_addr_ton": consts.SMPP_TON_INTL,
            "source_addr_npi": consts.SMPP_NPI_ISDN,
            "source_addr": config.SOURCE_ADDR,
            "dest_addr_ton": consts.SMPP_TON_INTL,
            "dest_addr_npi": consts.SMPP_NPI_ISDN,
            "destination_addr": "+8618279230916",
            "esm_class": 0,
            "protocol_id": consts.SMPP_PID_DEFAULT,
            "priority_flag": 0,
            "schedule_delivery_time": consts.NULL_BYTE,
            "validity_period": consts.NULL_BYTE,
            "registered_delivery": consts.SMPP_SMSC_DELIVERY_RECEIPT_BOTH,
            "replace_if_present_flag": 0,
            "data_coding": self.data_coding,
            "sm_default_msg_id": 0,
            "short_message": message
        }
        self.base_send_sm("submit_sm", **body)

    def parse_submit_sm_resp(self, resp, command_name):
        message_id = resp[16:-1]
        pdu = get_pdu(command_name)(message_id=message_id)
        resp_data = pdu.unpack(resp)
        pdu.command_length, pdu.command_id, pdu.command_status, pdu.sequence_number, pdu.message_id = resp_data[:-1]
        if pdu.sequence_number == self.sequence_number and pdu.command_status == consts.SMPP_ESME_ROK:
            self.logger.info(f"发送消息成功,{pdu}")
            self.last_message_id = pdu.message_id.decode()

    def data_sm(self, message):
        body = {
            "service_type": consts.NULL_BYTE,
            "source_addr_ton": consts.SMPP_TON_INTL,
            "source_addr_npi": consts.SMPP_NPI_ISDN,
            "source_addr": config.SOURCE_ADDR,
            "dest_addr_ton": consts.SMPP_TON_INTL,
            "dest_addr_npi": consts.SMPP_NPI_ISDN,
            "destination_addr": config.DESTINATION_ADDR,
            "esm_class": consts.NULL_BYTE,
            "registered_delivery": consts.SMPP_SMSC_DELIVERY_RECEIPT_BOTH,
            "data_coding": self.data_coding,
            "short_message": message
        }
        self.base_send_sm("data_sm", **body)

    def parse_data_sm_resp(self, resp, command_name):
        message_id = resp[16:-1]
        pdu = get_pdu(command_name)(message_id=message_id)
        resp_data = pdu.unpack(resp)
        pdu.command_length, pdu.command_id, pdu.command_status, pdu.sequence_number, pdu.message_id = resp_data[:-1]
        if pdu.sequence_number == self.sequence_number and pdu.command_status == consts.SMPP_ESME_ROK:
            self.logger.info(f"发送消息成功,{pdu}")

    def parse_deliver_sm(self, resp, command_name):
        sm_length = resp[56]
        # short_message = resp[57:57 + sm_length]
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
            # optional_param_type = struct.unpack(">H", pdu.optional_params[:2])[0]
            # optional_param_name = get_optional_param_name(optional_param_type)
            # print(optional_param_name)
            optional_param_length = struct.unpack(">H", pdu.optional_params[2:4])[0]
            # print(optional_param_length)
            payload = pdu.optional_params[4:4 + optional_param_length]
            data = payload[94:-9]
            print(data.decode())
        if pdu.command_status == consts.SMPP_ESME_ROK:
            self.deliver_sm_resp(pdu.sequence_number)

    def deliver_sm_resp(self, sequence_number):
        command_name = "deliver_sm_resp"
        command_id = get_command_id(command_name)
        pdu = get_pdu(command_name)(command_id=command_id, command_status=0, sequence_number=sequence_number)
        data = pdu.pack()
        self.client.sendall(data)

    def query_sm(self, message_id):
        body = {
            'message_id': message_id,
            'source_addr_ton': consts.SMPP_TON_INTL,
            "source_addr_npi": consts.SMPP_NPI_ISDN,
            'source_addr': config.SOURCE_ADDR,
        }
        self.base_send_sm("query_sm", **body)

    def parse_query_sm_resp(self, resp, command_name):
        message_id = resp[16:-3]
        pdu = get_pdu(command_name)(message_id=message_id)
        resp_data = pdu.unpack(resp)
        pdu.command_length, pdu.command_id, pdu.command_status, pdu.sequence_number, pdu.message_id, pdu.final_date, \
            pdu.message_state, pdu.error_code = resp_data
        if pdu.sequence_number == self.sequence_number:
            self.logger.info(f"消息状态:{pdu}")

    def cancel_sm(self, message_id):
        body = {
            "service_type": consts.NULL_BYTE,
            'message_id': message_id,
            'source_addr_ton': consts.SMPP_TON_INTL,
            "source_addr_npi": consts.SMPP_NPI_ISDN,
            'source_addr': config.SOURCE_ADDR,
            "dest_addr_ton": consts.SMPP_TON_INTL,
            "dest_addr_npi": consts.SMPP_NPI_ISDN,
            "destination_addr": config.DESTINATION_ADDR,
        }
        self.base_send_sm("cancel_sm", **body)

    def parse_cancel_sm_resp(self, resp, command_name):
        pdu = self.parse_base_resp(resp, command_name)
        if pdu.sequence_number == self.sequence_number:
            self.logger.info(f"{command_name}:{pdu}")

    def replace_sm(self, message_id, new_message):
        body = {
            'message_id': message_id,
            'source_addr_ton': consts.SMPP_TON_INTL,
            "source_addr_npi": consts.SMPP_NPI_ISDN,
            'source_addr': config.SOURCE_ADDR,
            'schedule_delivery_time': 0,
            'validity_period': 0,
            'registered_delivery': consts.SMPP_SMSC_DELIVERY_RECEIPT_BOTH,
            'sm_default_msg_id': 0,
            'short_message': new_message,
            "data_coding": self.data_coding
        }
        self.base_send_sm("replace_sm", **body)

    def parse_replace_sm_resp(self, resp, command_name):
        pdu = self.parse_base_resp(resp, command_name)
        if pdu.sequence_number == self.sequence_number:
            self.logger.info(f"{command_name}:{pdu}")

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
        if pdu.sequence_number == self.sequence_number:
            if pdu.command_status != consts.SMPP_ESME_ROK:
                self.client_state = consts.SMPP_CLIENT_STATE_OPEN

    def parse_generic_nack(self, resp, command_name):
        pdu = self.parse_base_resp(resp, command_name)
        if pdu.sequence_number == self.sequence_number:
            print(command_name, pdu)

    def parse_alert_notification(self, resp):
        sm_length = resp[56]
        # short_message = resp[57:57 + sm_length]
        optional_params = resp[57 + sm_length:]
        body = {
            "source_addr": config.SOURCE_ADDR,
            "esme_addr": config.ESME_ADDR,
            "sm_length": sm_length,
            "optional_params": optional_params
        }
        pdu = get_pdu("alert_notification")(**body)
        resp_data = pdu.unpack(resp)
        pdu.command_length, pdu.command_id, pdu.command_status, pdu.sequence_number = resp_data[:4]
        pdu.optional_params = resp_data[-1]
        if sm_length != 0:
            pdu.short_message = resp_data[-2]
        else:
            pdu.optional_params = resp_data[-1]
            # optional_param_type = struct.unpack(">H", pdu.optional_params[:2])[0]
            # optional_param_name = get_optional_param_name(optional_param_type)
            # print(optional_param_name)
            optional_param_length = struct.unpack(">H", pdu.optional_params[2:4])[0]
            # print(optional_param_length)
            payload = pdu.optional_params[4:4 + optional_param_length]
            data = payload[94:-9]
            print(data.decode())
        if pdu.command_status == consts.SMPP_ESME_ROK:
            self.deliver_sm_resp(pdu.sequence_number)

    def fuzz(self, count, loop, interval, command_name="bind_transmitter"):
        if command_name != "bind_transceiver":
            self.bind()
        for i in range(loop):
            for _ in range(count):
                fuzz_data = {
                    "bind_transceiver": fuzzer.fuzz_bind_transceiver(),
                    "submit_sm": fuzzer.fuzz_submit_sm(),
                    "enquire_link": fuzzer.fuzz_enquire_link(),
                    "unbind": fuzzer.fuzz_unbind(),
                    "query_sm": fuzzer.fuzz_query_sm(),
                    "cancel_sm": fuzzer.fuzz_cancel_sm(),
                    "replace_sm": fuzzer.fuzz_replace_sm(),
                    "deliver_sm_resp": fuzzer.fuzz_deliver_sm_resp(),
                }
                data = fuzz_data[command_name]
                self.logger.info(f"Starting fuzz {self.fuzz_num}")
                try:
                    self.client.sendall(data)
                    self.logger.info(f"Fuzz {self.fuzz_num} send successfully")
                except BrokenPipeError as e:
                    self.logger.error(f"Fuzz {self.fuzz_num} BrokenPipeError: {e}")
                    with open(f"./data/err_send_data/{self.fuzz_num}", 'wb') as f:
                        f.write(data)
                    self.connect()
                    self.bind()
                    self.client.sendall(data)
                except Exception as e:
                    self.logger.error(f"Fuzz {self.fuzz_num} failed with error: {e}")
                    with open(f"./data/err_send_data/{self.fuzz_num}", 'wb') as f:
                        f.write(data)
                finally:
                    self.fuzz_num += 1
                    time.sleep(interval)
