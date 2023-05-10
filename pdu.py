import struct
import gsm0338

import consts
import command


def get_tag(name):
    return consts.OPTIONAL_PARAMS.get(name)


def get_pdu(command_name):
    """生成PDU"""
    try:
        return {
            'bind_transmitter': BindTransmitterPDU,
            'bind_transmitter_resp': BindTransmitterRespPDU,
            'bind_receiver': BindReceiverPDU,
            'bind_receiver_resp': BindReceiverRespPDU,
            'bind_transceiver': BindTransceiverPDU,
            'bind_transceiver_resp': BindTransceiverRespPDU,
            'data_sm': DataSMPDU,
            'data_sm_resp': DataSMRespPDU,
            'generic_nack': GenericNAckPDU,
            'submit_sm': SubmitSMPDU,
            'submit_sm_resp': SubmitSMRespPDU,
            'deliver_sm': DeliverSMPDU,
            'deliver_sm_resp': DeliverSMRespPDU,
            'query_sm': QuerySMPDU,
            'query_sm_resp': QuerySMRespPDU,
            'cancel_sm': CancelSMPDU,
            'cancel_sm_resp': CancelSMRespPDU,
            'replace_sm': ReplaceSMPDU,
            'replace_sm_resp': ReplaceSMRespPDU,
            'unbind': UnbindPDU,
            'unbind_resp': UnbindRespPDU,
            'enquire_link': EnquireLinkPDU,
            'enquire_link_resp': EnquireLinkRespPDU,
            'alert_notification': AlertNotificationPDU,
        }[command_name]
    except KeyError:
        raise Exception('Command "%s" is not supported' % command_name)


class PDU:
    def __init__(self, command_id, command_status, sequence_number):
        self.command_id = command_id  # Operation
        self.command_status = command_status
        self.sequence_number = sequence_number
        self.struct = struct.Struct(">LLLL")
        self.command_length = self.struct.size

    def __str__(self):
        return f"PDU(command_length:{self.command_length},operation:{command.get_command_name(self.command_id)}," + \
            f"command_status:'{consts.DESCRIPTIONS.get(self.command_status)}',sequence_number:{self.sequence_number})"

    def pack(self):
        data = self.struct.pack(self.command_length, self.command_id, self.command_status, self.sequence_number)
        return data

    def unpack(self, resp):
        return self.struct.unpack(resp)


class Param:
    def __init__(self, type, size=None, min=None, max=None, len_field=None):
        self.type = type
        self.size = size
        self.min = min
        self.max = max


class BindTransmitterPDU(PDU):
    """
    ESME转发端
    """
    params = {
        'system_id': Param(type=str, max=16),
        'password': Param(type=str, max=9),
        'system_type': Param(type=str, max=13),
        'interface_version': Param(type=int, size=1),
        'addr_ton': Param(type=int, size=1),
        'addr_npi': Param(type=int, size=1),
        'address_range': Param(type=str, max=41),
    }

    def __init__(self, command_id, command_status, sequence_number, system_id, password):
        super().__init__(command_id, command_status, sequence_number)
        self.system_id = system_id
        self.password = password if len(password) < 9 else password[:8]
        self.system_type = consts.NULL_BYTE
        self.interface_version = consts.SMPP_VERSION_34
        self.addr_ton = consts.NULL_BYTE
        self.addr_npi = consts.NULL_BYTE
        self.address_range = consts.NULL_BYTE
        self.struct = struct.Struct(f">LLLL{len(self.system_id) + 1}s{len(self.password) + 1}s5s")
        self.command_length = self.struct.size

    def pack(self):
        data = self.struct.pack(self.command_length, self.command_id, self.command_status, self.sequence_number,
                                self.system_id.encode() + b'\x00', self.password.encode() + b'\x00',
                                self.system_type + self.interface_version.to_bytes(1,
                                                                                   'big') + self.addr_ton + self.addr_npi + self.address_range)
        return data


class BindTransmitterRespPDU(PDU):
    def __init__(self, command_id=None, command_status=None, sequence_number=None, system_id=None):
        super().__init__(command_id, command_status, sequence_number)
        self.system_id = system_id
        self.struct = struct.Struct(f">LLLL{len(self.system_id)}sc")
        self.command_length = self.struct.size

    def __str__(self):
        return f"PDU(command_length:{self.command_length}, operation:{command.get_command_name(self.command_id)},\
        command_status:{self.command_status}, sequence_number:{self.sequence_number},\
        system_id:{self.system_id.decode('ascii')})"


class BindReceiverPDU(BindTransmitterPDU):
    """
    ESME接收端
    """
    pass


class BindReceiverRespPDU(BindTransmitterRespPDU):
    pass


class BindTransceiverPDU(BindTransmitterPDU):
    """
    ESME收发端
    """
    pass


class BindTransceiverRespPDU(BindTransmitterRespPDU):
    pass


class GenericNAckPDU(PDU):
    pass


class SubmitSMPDU(PDU):
    params = {
        'service_type': Param(type=str, max=6),
        'source_addr_ton': Param(type=int, size=1),
        'source_addr_npi': Param(type=int, size=1),
        'source_addr': Param(type=str, max=21),
        'dest_addr_ton': Param(type=int, size=1),
        'dest_addr_npi': Param(type=int, size=1),
        'destination_addr': Param(type=str, max=21),
        'esm_class': Param(type=int, size=1),
        'protocol_id': Param(type=int, size=1),
        'priority_flag': Param(type=int, size=1),
        'schedule_delivery_time': Param(type=str, max=17),
        'validity_period': Param(type=str, max=17),
        'registered_delivery': Param(type=int, size=1),
        'replace_if_present_flag': Param(type=int, size=1),
        'data_coding': Param(type=int, size=1),
        'sm_default_msg_id': Param(type=int, size=1),
        'sm_length': Param(type=int, size=1),
        'short_message': Param(type=str, max=254, len_field='sm_length'),

        # Optional params
        'user_message_reference': Param(type=int, size=2),
        'source_port': Param(type=int, size=2),
        'source_addr_subunit': Param(type=int, size=2),
        'destination_port': Param(type=int, size=2),
        'dest_addr_subunit': Param(type=int, size=1),
        'sar_msg_ref_num': Param(type=int, size=2),
        'sar_total_segments': Param(type=int, size=1),
        'sar_segment_seqnum': Param(type=int, size=1),
        'more_messages_to_send': Param(type=int, size=1),
        'payload_type': Param(type=int, size=1),
        'message_payload': Param(type=str, max=260),
        'privacy_indicator': Param(type=int, size=1),
        'callback_num': Param(type=str, min=4, max=19),
        'callback_num_pres_ind': Param(type=int, size=1),
        'source_subaddress': Param(type=str, min=2, max=23),
        'dest_subaddress': Param(type=str, min=2, max=23),
        'user_response_code': Param(type=int, size=1),
        'display_time': Param(type=int, size=1),
        'sms_signal': Param(type=int, size=2),
        'ms_validity': Param(type=int, size=1),
        'ms_msg_wait_facilities': Param(type=int, size=1),
        'number_of_messages': Param(type=int, size=1),
        'alert_on_message_delivery': Param(type=str),
        'language_indicator': Param(type=int, size=1),
        'its_reply_type': Param(type=int, size=1),
        'its_session_info': Param(type=int, size=2),
        'ussd_service_op': Param(type=int, size=1),
    }

    def __init__(self, command_id, command_status, sequence_number, source_addr, destination_addr, data_coding,
                 message, *args):
        super().__init__(command_id, command_status, sequence_number)
        # Default
        self.service_type = consts.NULL_BYTE
        self.source_addr_ton = consts.SMPP_TON_INTL
        self.source_addr_npi = consts.SMPP_NPI_ISDN
        self.source_addr = source_addr
        self.dest_addr_ton = consts.SMPP_TON_INTL
        self.dest_addr_npi = consts.SMPP_NPI_ISDN
        self.destination_addr = destination_addr
        self.esm_class = consts.NULL_BYTE
        self.protocol_id = consts.SMPP_PID_DEFAULT
        self.priority_flag = consts.NULL_BYTE
        self.schedule_delivery_time = consts.NULL_BYTE
        self.validity_period = consts.NULL_BYTE
        self.registered_delivery = consts.SMPP_SMSC_DELIVERY_RECEIPT_BOTH
        self.replace_if_present_flag = consts.NULL_BYTE
        self.data_coding = data_coding
        self.sm_default_msg_id = consts.NULL_BYTE
        self.sm_length = None
        self.short_message = message
        self.message_bytes = None

    def pack(self):
        if self.data_coding == consts.SMPP_ENCODING_ISO10646:
            self.message_bytes = self.short_message.encode("utf-16be")
        elif self.data_coding == consts.SMPP_ENCODING_DEFAULT:
            encoder = gsm0338.Codec()
            self.message_bytes = encoder.encode(self.short_message)[0]
        self.sm_length = len(self.message_bytes)
        self.struct = struct.Struct(
            f">LLLLcBB{len(self.source_addr) + 1}sBB{len(self.destination_addr) + 1}scBcccBcBcB{self.sm_length}s")
        self.command_length = self.struct.size

        data = self.struct.pack(self.command_length, self.command_id, self.command_status, self.sequence_number,
                                self.service_type, self.source_addr_ton, self.source_addr_npi,
                                self.source_addr.encode() + b'\x00', self.dest_addr_ton, self.dest_addr_npi,
                                self.destination_addr.encode() + b'\x00', self.esm_class, self.protocol_id,
                                self.priority_flag, self.schedule_delivery_time, self.validity_period,
                                self.registered_delivery, self.replace_if_present_flag,
                                self.data_coding, self.sm_default_msg_id, self.sm_length, self.message_bytes)
        return data


class SubmitSMRespPDU(PDU):
    def __init__(self, command_id=None, command_status=None, sequence_number=None, message_id=None):
        super().__init__(command_id, command_status, sequence_number)
        self.message_id = message_id
        self.struct = struct.Struct(f">LLLL{len(self.message_id)}sc")

    def __str__(self):
        return f"PDU(length:{self.struct.size}, operation:{command.get_command_name(self.command_id)},\
        command_status:{consts.DESCRIPTIONS.get(self.command_status)}, sequence_number:{self.sequence_number},\
        message_id:{self.message_id})"


class DeliverSMPDU(PDU):
    def __init__(self, command_id=None, command_status=None, sequence_number=None, source_addr=None,
                 destination_addr=None, data_coding=None, short_message=None, sm_length=None,
                 optional_params=None):
        super().__init__(command_id, command_status, sequence_number)
        self.service_type = None
        self.source_addr_ton = None
        self.source_addr_npi = None
        self.source_addr = source_addr
        self.dest_addr_ton = None
        self.dest_addr_npi = None
        self.destination_addr = destination_addr
        self.esm_class = None
        self.protocol_id = None
        self.priority_flag = None
        self.schedule_delivery_time = None
        self.validity_period = None
        self.registered_delivery = None
        self.replace_if_present_flag = None
        self.data_coding = data_coding
        self.sm_default_msg_id = None
        self.sm_length = sm_length
        self.short_message = short_message
        self.message_bytes = None
        self.optional_params = optional_params
        self.struct = struct.Struct(
            f">LLLLcBB{len(self.source_addr) + 1}sBB{len(self.destination_addr) + 1}scBcccBcBcB{self.sm_length}s{len(self.optional_params)}s")
        self.command_length = self.struct.size

    def __str__(self):
        return super().__str__()[
               :-1] + f",source_addr={self.source_addr},destination_addr={self.destination_addr},data_coding={self.data_coding})"


class DeliverSMRespPDU(PDU):
    def __init__(self, command_id, command_status, sequence_number):
        super().__init__(command_id, command_status, sequence_number)
        self.message_id = consts.NULL_BYTE
        self.struct = struct.Struct(f">LLLLc")
        self.command_length = self.struct.size

    def pack(self):
        data = self.struct.pack(self.command_length, self.command_id, self.command_status, self.sequence_number,
                                self.message_id)
        return data


class DataSMPDU(PDU):
    def __init__(self, command_id, command_status, sequence_number, source_addr, destination_addr, data_coding,
                 message):
        super().__init__(command_id, command_status, sequence_number)
        # Default
        self.service_type = consts.NULL_BYTE
        self.source_addr_ton = consts.SMPP_TON_INTL
        self.source_addr_npi = consts.SMPP_NPI_ISDN
        self.source_addr = source_addr
        self.dest_addr_ton = consts.SMPP_TON_INTL
        self.dest_addr_npi = consts.SMPP_NPI_ISDN
        self.destination_addr = destination_addr
        self.esm_class = consts.NULL_BYTE
        self.registered_delivery = consts.SMPP_SMSC_DELIVERY_RECEIPT_BOTH
        self.data_coding = data_coding
        self.message = message
        self.message_bytes = None
        self.message_length = None
        self.optional_params = None

    def pack(self):
        if self.data_coding == consts.SMPP_ENCODING_ISO10646:
            self.message_bytes = self.message.encode("utf-16be")
        elif self.data_coding == consts.SMPP_ENCODING_DEFAULT:
            encoder = gsm0338.Codec()
            self.message_bytes = encoder.encode(self.message)[0]
        tag = get_tag("message_payload")
        print(tag)
        payload = self.message_bytes + b'\x1b\x3c\x54\x52\x49\x41\x4c\x1b\x3e'
        payload_length = len(payload)

        self.struct = struct.Struct(
            f">LLLLcBB{len(self.source_addr) + 1}sBB{len(self.destination_addr) + 1}scBBHH{payload_length}s")
        self.command_length = self.struct.size

        data = self.struct.pack(self.command_length, self.command_id, self.command_status, self.sequence_number,
                                self.service_type, self.source_addr_ton, self.source_addr_npi,
                                self.source_addr.encode() + b'\x00', self.dest_addr_ton, self.dest_addr_npi,
                                self.destination_addr.encode() + b'\x00', self.esm_class, self.registered_delivery,
                                self.data_coding, tag, payload_length, payload)
        return data


class DataSMRespPDU(SubmitSMRespPDU):
    pass


class QuerySMPDU(PDU):
    params = {
        'message_id': Param(type=str, max=65),
        'source_addr_ton': Param(type=int, size=1),
        'source_addr_npi': Param(type=int, size=1),
        'source_addr': Param(type=str, max=21),
    }

    def __init__(self, command_id, command_status, sequence_number, source_addr, message_id):
        super().__init__(command_id, command_status, sequence_number)
        # 同submit_sm一样
        self.message_id = message_id
        self.source_addr_ton = consts.SMPP_TON_INTL
        self.source_addr_npi = consts.SMPP_NPI_ISDN
        self.source_addr = source_addr

    def pack(self):
        self.struct = struct.Struct(
            f">LLLL{len(self.message_id) + 1}sBB{len(self.source_addr) + 1}s")
        self.command_length = self.struct.size

        data = self.struct.pack(self.command_length, self.command_id, self.command_status, self.sequence_number,
                                self.message_id.encode() + b'\x00', self.source_addr_ton, self.source_addr_npi,
                                self.source_addr.encode() + b'\x00')
        return data


class QuerySMRespPDU(PDU):
    params = {
        'message_id': Param(type=str, max=65),
        'final_date': Param(type=str, max=17),
        'message_state': Param(type=int, size=1),
        'error_code': Param(type=int, size=1),
    }

    def __init__(self, command_id=None, command_status=None, sequence_number=None, message_id=None):
        super().__init__(command_id, command_status, sequence_number)
        self.message_id = message_id
        self.final_date = None
        self.message_state = None
        self.error_code = None
        self.struct = struct.Struct(f">LLLL{len(self.message_id)}sBBB")

    def __str__(self):
        return f"PDU(length:{self.struct.size}, operation:{command.get_command_name(self.command_id)},\
               command_status:{consts.DESCRIPTIONS.get(self.command_status)},\
               sequence_number:{self.sequence_number},message_id:{self.message_id})"


class CancelSMPDU(PDU):
    params = {
        'message_id': Param(type=str, max=65),
        'source_addr_ton': Param(type=int, size=1),
        'source_addr_npi': Param(type=int, size=1),
        'source_addr': Param(type=str, max=21),
    }

    def __init__(self, command_id, command_status, sequence_number, message_id, source_addr, destination_addr):
        super().__init__(command_id, command_status, sequence_number)
        # 同submit_sm一样
        self.service_type = consts.NULL_BYTE
        self.message_id = message_id
        self.source_addr_ton = consts.SMPP_TON_INTL
        self.source_addr_npi = consts.SMPP_NPI_ISDN
        self.source_addr = source_addr
        self.dest_addr_ton = consts.SMPP_TON_INTL
        self.dest_addr_npi = consts.SMPP_NPI_ISDN
        self.destination_addr = destination_addr

    def pack(self):
        self.struct = struct.Struct(
            f">LLLLc{len(self.message_id) + 1}sBB{len(self.source_addr) + 1}sBB{len(self.destination_addr) + 1}s")
        self.command_length = self.struct.size

        data = self.struct.pack(self.command_length, self.command_id, self.command_status, self.sequence_number,
                                self.service_type, self.message_id.encode() + b'\x00',
                                self.source_addr_ton, self.source_addr_npi, self.source_addr.encode() + b'\x00',
                                self.dest_addr_ton, self.dest_addr_npi, self.destination_addr.encode() + b'\x00')
        return data


class CancelSMRespPDU(PDU):
    def __init__(self, command_id=None, command_status=None, sequence_number=None):
        super().__init__(command_id, command_status, sequence_number)


class ReplaceSMPDU(PDU):
    hearer = {
        'message_id': Param(type=str, max=65),
        'source_addr_ton': Param(type=int, size=1),
        'source_addr_npi': Param(type=int, size=1),
        'source_addr': Param(type=str, max=21),
        'schedule_delivery_time': Param(type=str, max=17),
        'validity_period': Param(type=str, max=17),
        'registered_delivery': Param(type=int, size=1),
        'sm_default_msg_id': Param(type=int, size=1),
        'sm_length': Param(type=int, size=1),
        'short_message': Param(type=str, max=254, len_field='sm_length'),
    }

    def __init__(self, command_id, command_status, sequence_number, message_id, source_addr, new_message, data_coding):
        super().__init__(command_id, command_status, sequence_number)
        # Default
        self.message_id = message_id
        self.source_addr_ton = consts.SMPP_TON_INTL
        self.source_addr_npi = consts.SMPP_NPI_ISDN
        self.source_addr = source_addr
        self.schedule_delivery_time = 0
        self.validity_period = 0
        self.registered_delivery = consts.SMPP_SMSC_DELIVERY_RECEIPT_BOTH
        self.sm_default_msg_id = 0
        self.sm_length = None
        self.short_message = new_message
        self.data_coding = data_coding
        self.message_bytes = None

    def pack(self):
        if self.data_coding == consts.SMPP_ENCODING_ISO10646:
            self.message_bytes = self.short_message.encode("utf-16be")
        elif self.data_coding == consts.SMPP_ENCODING_DEFAULT:
            encoder = gsm0338.Codec()
            self.message_bytes = encoder.encode(self.short_message)[0]
        self.sm_length = len(self.message_bytes)
        self.struct = struct.Struct(
            f">LLLL{len(self.message_id) + 1}sBB{len(self.source_addr) + 1}sBBBBB{self.sm_length}s")
        self.command_length = self.struct.size

        data = self.struct.pack(self.command_length, self.command_id, self.command_status, self.sequence_number,
                                self.message_id.encode() + b'\x00', self.source_addr_ton, self.source_addr_npi,
                                self.source_addr.encode() + b'\x00', self.schedule_delivery_time, self.validity_period,
                                self.registered_delivery, self.sm_default_msg_id, self.sm_length, self.message_bytes)
        return data


class ReplaceSMRespPDU(PDU):
    def __init__(self, command_id=None, command_status=None, sequence_number=None):
        super().__init__(command_id, command_status, sequence_number)


class UnbindPDU(PDU):
    pass


class UnbindRespPDU(PDU):
    def __init__(self, command_id=None, command_status=None, sequence_number=None):
        super().__init__(command_id, command_status, sequence_number)


class EnquireLinkPDU(PDU):
    pass


class EnquireLinkRespPDU(PDU):
    def __init__(self, command_id=None, command_status=None, sequence_number=None):
        super().__init__(command_id, command_status, sequence_number)


class AlertNotificationPDU(PDU):
    params = {
        'source_addr_ton': Param(type=int, size=1),
        'source_addr_npi': Param(type=int, size=1),
        'source_addr': Param(type=str, max=21),
        'esme_addr_ton': Param(type=int, size=1),
        'esme_addr_npi': Param(type=int, size=1),
        'esme_addr': Param(type=str, max=21),

        # Optional params
        'ms_availability_status': Param(type=int, size=1),
    }

    def __init__(self, command_id=None, command_status=None, sequence_number=None, source_addr=None,
                 esme_addr=None, optional_params=None):
        super().__init__(command_id, command_status, sequence_number)
        self.source_addr_ton = None
        self.source_addr_npi = None
        self.source_addr = source_addr
        self.esme_addr_ton = None
        self.esme_addr_npi = None
        self.esme_addr = esme_addr
        self.optional_params = optional_params
        self.struct = struct.Struct(
            f">LLLLBB{len(self.source_addr) + 1}sBB{len(self.esme_addr) + 1}s{len(self.optional_params)}s")
        self.command_length = self.struct.size

    def __str__(self):
        return super().__str__()[:-1] + f",source_addr={self.source_addr},esme_addr={self.esme_addr})"
