import struct
import gsm0338

import config
import consts
from command import get_command_name


class Param:
    def __init__(self, type=None, size=None, min=None, max=None, len_field=None):
        self.type = type
        self.size = size
        self.min = min
        self.max = max
        self.len_field = len_field


class TLV:
    """
    可选参数
    """
    body = {
        "tag": Param(type=int, size=2),
        "length": Param(type=int, size=2),
        "value": Param(len_field="length")
    }

    def __init__(self, tag=None, type=None, length=1, value=None, max=None):
        self.tag = tag
        if type is None:
            type = int
        self.type = type
        self.length = length
        self.value = value
        self.max = max
        if self.max:
            self.length = None

    def get_tag(self):
        return consts.OPTIONAL_PARAMS.get(self.tag)


class PDU:
    header = {
        "command_length": Param(type=int, size=4),
        "command_id": Param(type=int, size=4),
        "command_status": Param(type=int, size=4),
        "sequence_number": Param(type=int, size=4),
    }

    def __init__(self, grammar=">4L"):
        self.grammar = grammar
        self._add_grammer()
        # print(self.grammar)
        self.struct = struct.Struct(self.grammar)
        self.command_length = self.struct.size
        self.pack_param = []

    def _set_vals(self, d):
        for k, v in d.items():
            setattr(self, k, v)

    def _add_grammer(self):
        if not getattr(self, 'body', None):
            return
        for k, v in self.body.items():
            tlv = v.type
            if type(tlv) == TLV:
                s = '2H'
                if tlv.type == int:
                    s += consts.INT_PACK_FORMATS[tlv.length]
                elif tlv.type == str:
                    tlv_len = tlv.length if tlv.length else None
                    if k == 'message_payload':
                        tlv_len = len(self.message_bytes)
                    elif tlv.max:
                        tlv_len = len(getattr(self, k))
                    if tlv_len is not None:
                        s += f'{tlv_len}s'
                self.grammar += s

    def gen_pack_param(self):
        for k, v in self.header.items():
            param = getattr(self, k)
            self.pack_param.append(param)
        if not getattr(self, 'body', None):
            return
        for k, v in self.body.items():
            param = getattr(self, k)
            tlv = v.type
            if v.type == str and type(param) == str:
                param = param.encode()
                if k in config.ADD_NULL_PARAMS:
                    param += b'\x00'
                if k == "short_message":
                    param = self.message_bytes
            elif type(tlv) == TLV:
                self.pack_param.append(TLV(k).get_tag())
                if k == 'message_payload':
                    param = self.message_bytes
                elif tlv.type == str and type(param) == str:
                    param = param.encode()
                tlv_len = tlv.length if tlv.length else len(param)
                self.pack_param.append(tlv_len)
            if param != b'':
                self.pack_param.append(param)

    def pack(self):
        self.gen_pack_param()
        # print(self.grammar)
        # print(self.pack_param)
        data = self.struct.pack(*self.pack_param)
        return data

    def unpack(self, resp):
        # print(len(resp), resp)
        return self.struct.unpack(resp)

    def gen_message_bytes(self):
        msg = self.short_message if not getattr(self, 'message_payload', None) else self.message_payload
        if self.data_coding == consts.ENCODING_ISO10646:
            return msg.encode("utf-16be")
        elif self.data_coding == consts.ENCODING_DEFAULT:
            return gsm0338.Codec().encode(msg)[0]

    def __str__(self):
        s = 'PDU('
        for k in self.header:
            v = getattr(self, k)
            if k == 'command_id':
                v = get_command_name(v)
            s += f"{k}:{v},"
        if getattr(self, 'body', None):
            for k in self.body:
                s += f"{k}:{getattr(self, k)},"
        return s[:-1] + ')'


class HeaderPDU(PDU):
    def __init__(self, **kwargs):
        self._set_vals(kwargs)
        super().__init__()


class BindTransmitterPDU(PDU):
    """
    ESME转发端
    """
    body = {
        'system_id': Param(type=str, max=16),
        'password': Param(type=str, max=9),
        'system_type': Param(type=str, max=13),
        'interface_version': Param(type=int, size=1),
        'addr_ton': Param(type=int, size=1),
        'addr_npi': Param(type=int, size=1),
        'address_range': Param(type=str, max=41),
    }

    def __init__(self, **kwargs):
        self._set_vals(kwargs)
        grammar = f">4L{len(self.system_id) + 1}s{len(self.password) + 1}s{len(self.system_type) + 1}s3Bc"
        super().__init__(grammar)


class BindTransmitterRespPDU(PDU):
    body = {
        "system_id": Param(type=str),
        # Optional params
        # "sc_interface_version": Param(type=TLV())
    }

    def __init__(self, **kwargs):
        self._set_vals(kwargs)
        grammar = f">4L{len(self.system_id)}sc"
        super().__init__(grammar)


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


class GenericNAckPDU(HeaderPDU):
    pass


class SubmitSMPDU(PDU):
    body = {
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
        'user_message_reference': Param(type=TLV(length=2)),
        # 'source_port': Param(type=TLV(length=2)),
        # 'source_addr_subunit': Param(type=TLV()),
        # 'destination_port': Param(type=TLV(length=2)),
        # 'dest_addr_subunit': Param(type=TLV()),
        # 'sar_msg_ref_num': Param(type=TLV()),
        # 'sar_total_segments': Param(type=TLV()),
        # 'sar_segment_seqnum': Param(type=TLV()),
        # 'more_messages_to_send': Param(type=TLV(type=str)),
        # 'payload_type': Param(type=TLV()),
        'message_payload': Param(type=TLV(type=str, max=64 * 1024)),
        # 'privacy_indicator': Param(type=TLV()),
        # 'callback_num': Param(type=TLV(type=str)),
        # 'callback_num_pres_ind': Param(type=TLV(type=str)),
        # 'callback_num_atag': Param(type=TLV(type=str)),
        # 'source_subaddress': Param(type=TLV(type=str, max=23)),
        # 'dest_subaddress': Param(type=TLV(type=str, max=23)),
        # 'user_response_code': Param(type=TLV()),
        # 'display_time': Param(type=TLV()),
        # 'sms_signal': Param(type=TLV(type=str, length=2)),
        # 'ms_validity': Param(type=TLV()),
        # 'ms_msg_wait_facilities': Param(type=TLV(type=str)),
        # 'number_of_messages': Param(type=TLV(type=str)),
        # 'alert_on_message_delivery': Param(type=TLV(type=str, length=0)),
        # 'language_indicator': Param(type=TLV()),
        # 'its_reply_type': Param(type=TLV(type=str)),
        # 'its_session_info': Param(type=TLV(type=str, length=2)),
        # 'ussd_service_op': Param(type=TLV(type=str)),
    }

    def __init__(self, **kwargs):
        self._set_vals(kwargs)
        self.message_bytes = self.gen_message_bytes()
        self.sm_length = len(self.message_bytes)
        if getattr(self, 'message_payload', None):
            self.sm_length = 0
        grammar = f">4L{len(self.service_type)}s2B{len(self.source_addr) + 1}s2B{len(self.destination_addr) + 1}s" + \
                  f"3B2c5B{self.sm_length}s"
        super().__init__(grammar)


class SubmitSMRespPDU(PDU):
    body = {
        "message_id": Param(type=str)
    }

    def __init__(self, **kwargs):
        self._set_vals(kwargs)
        grammar = f">4L{len(self.message_id)}sc"
        super().__init__(grammar)


class SubmitMultiPDU(PDU):
    body = {
        'service_type': Param(type=str, max=6),
        'source_addr_ton': Param(type=int, size=1),
        'source_addr_npi': Param(type=int, size=1),
        'source_addr': Param(type=str, max=21),
        'number_of_dests': Param(type=int, size=1),
        'dest_addresses': Param(type=str, max=254),
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

        # # Optional params
        'user_message_reference': Param(type=TLV(length=2)),
        'source_port': Param(type=TLV()),
        'source_addr_subunit': Param(type=TLV()),
        'destination_port': Param(type=TLV()),
        'dest_addr_subunit': Param(type=TLV()),
        'sar_msg_ref_num': Param(type=TLV()),
        'sar_total_segments': Param(type=TLV()),
        'sar_segment_seqnum': Param(type=TLV()),
        'payload_type': Param(type=TLV()),
        'message_payload': Param(type=TLV(type=str)),
        'privacy_indicator': Param(type=TLV()),
        'callback_num': Param(type=TLV(type=str)),
        'callback_num_pres_ind': Param(type=TLV(type=str)),
        'callback_num_atag': Param(type=TLV(type=str)),
        'source_subaddress': Param(type=TLV(type=str, max=23)),
        'dest_subaddress': Param(type=TLV(type=str, max=23)),
        'display_time': Param(type=TLV()),
        'sms_signal': Param(type=TLV(type=str)),
        'ms_validity': Param(type=TLV()),
        'ms_msg_wait_facilities': Param(type=TLV(type=bytes)),
        'alert_on_message_delivery': Param(type=TLV(type=str, length=0)),
        'language_indicator': Param(type=TLV()),
        # # 目的地址定义
        # 'dest_flag': Param(type=int,size=1),
        # # SME_dest_address
        # 'dest_addr_ton': Param(type=int,size=1),
        # 'dest_addr_npi': Param(type=int,size=1),
        # 'destination_addr': Param(type=str,size=21),
        # # 分布显示定义
        # 'dl_name': Param(type=str,size=21)
    }

    def __init__(self, **kwargs):
        self._set_vals(kwargs)
        self.message_bytes = self.gen_message_bytes()
        self.sm_length = len(self.message_bytes)
        grammar = f">4L{len(self.service_type)}s2B{len(self.source_addr) + 1}sB{len(self.dest_addresses) + 1}s" + \
                  f"3B2c5B{self.sm_length}s"
        super().__init__(grammar)


class SubmitMultiRespPDU(PDU):
    body = {
        "message_id": Param(type=str, max=65),
        "no_unsuccess": Param(type=int, size=1),
        "unsuccess_smes": Param(type=str),
        # Optional params
        # 递送失败
        # 'dest_addr_ton': Param(type=int, size=1),
        # 'dest_addr_npi': Param(type=int, size=1),
        # 'destination_addr': Param(type=str, max=21),
        # 'error_status_code': Param(type=int, size=1),

    }

    def __init__(self, **kwargs):
        self._set_vals(kwargs)
        grammar = f">4L{len(self.message_id)}sB{len(self.unsuccess_smes)}s"
        super().__init__(grammar)


class DeliverSMPDU(PDU):
    body = {
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
        # 'user_message_reference': Param(type=TLV(length=2)),
        # 'source_port': Param(type=TLV()),
        # 'destination_port': Param(type=TLV()),
        # 'sar_msg_ref_num': Param(type=TLV()),
        # 'sar_total_segments': Param(type=TLV()),
        # 'sar_segment_seqnum': Param(type=TLV()),
        # 'user_response_code': Param(type=TLV()),
        # 'privacy_indicator': Param(type=TLV()),
        # 'payload_type': Param(type=TLV()),
        # 'message_payload': Param(type=TLV(type=str)),
        # 'callback_num': Param(type=TLV(type=str)),
        # 'source_subaddress': Param(type=TLV(type=str,max=23)),
        # 'dest_subaddress': Param(type=TLV(type=str,max=23)),
        # 'language_indicator': Param(type=TLV()),
        # 'its_session_info': Param(type=TLV(type=str)),
        # 'network_error_code': Param(type=TLV(type=str,length=3)),
        # 'message_state': Param(type=TLV(type=str)),
        # 'receipted_message_id': Param(type=TLV(type=str,max=65)),
    }

    def __init__(self, **kwargs):
        self._set_vals(kwargs)
        grammar = f">4L3B{len(self.source_addr) + 1}sBB{len(self.destination_addr) + 1}scB3cBcBcB{self.sm_length}s" \
                  + f"{len(self.optional_params)}s"
        super().__init__(grammar)
        self.service_type = None
        self.source_addr_ton = None
        self.source_addr_npi = None
        self.dest_addr_ton = None
        self.dest_addr_npi = None
        self.esm_class = None
        self.protocol_id = None
        self.priority_flag = None
        self.schedule_delivery_time = None
        self.validity_period = None
        self.registered_delivery = None
        self.replace_if_present_flag = None
        self.data_coding = None
        self.sm_default_msg_id = None
        self.short_message = None
        self.message_bytes = None


class DeliverSMRespPDU(PDU):
    body = {
        "message_id": Param(type=str, size=1)
    }

    def __init__(self, **kwargs):
        self._set_vals(kwargs)
        grammar = f">4Lc"
        super().__init__(grammar)
        self.message_id = consts.NULL_BYTE


class DataSMPDU(PDU):
    body = {
        "service_type": Param(type=str, size=1),
        "source_addr_ton": Param(type=int, size=1),
        "source_addr_npi": Param(type=int, size=1),
        "source_addr": Param(type=str, max=21),
        "dest_addr_ton": Param(type=int, size=1),
        "dest_addr_npi": Param(type=int, size=1),
        "destination_addr": Param(type=str, max=21),
        "esm_class": Param(type=str, size=1),
        "registered_delivery": Param(type=int, size=1),
        "data_coding": Param(type=int, size=1),

        # # Optional params
        'source_port': Param(type=TLV()),
        'source_addr_subunit': Param(type=TLV()),
        'source_network_type': Param(type=TLV()),
        'source_bearer_type': Param(type=TLV()),
        'source_telematics_id': Param(type=TLV()),
        'destination_port': Param(type=TLV()),
        'dest_addr_subunit': Param(type=TLV()),
        'dest_network_type': Param(type=TLV()),
        'dest_bearer_type': Param(type=TLV()),
        'dest_telematics_id': Param(type=TLV(length=2)),
        'sar_msg_ref_num': Param(type=TLV()),
        'sar_total_segments': Param(type=TLV()),
        'sar_segment_seqnum': Param(type=TLV()),
        'more_messages_to_send': Param(type=TLV(type=str)),
        'qos_time_to_live': Param(type=TLV(length=4)),
        'payload_type': Param(type=TLV()),
        'message_payload': Param(type=TLV(type=str)),
        'set_dpf': Param(type=TLV()),
        'receipted_message_id': Param(type=TLV(type=str, max=65)),
        'message_state': Param(type=TLV(type=str)),
        'network_error_code': Param(type=TLV(type=str, length=3)),
        'user_message_reference': Param(type=TLV(length=2)),
        'privacy_indicator': Param(type=TLV()),
        'callback_num': Param(type=TLV(type=str)),
        'callback_num_pres_ind': Param(type=TLV(type=str)),
        'callback_num_pres_atag': Param(type=TLV(type=str)),
        'source_subaddress': Param(type=TLV(type=str, max=23)),
        'dest_subaddress': Param(type=TLV(type=str, max=23)),
        'user_response_code': Param(type=TLV()),
        'display_time': Param(type=TLV()),
        'sms_signal': Param(type=TLV(type=str)),
        'ms_validity': Param(type=TLV()),
        'ms_msg_wait_facilities': Param(type=TLV(type=bytes)),
        'number_of_messages': Param(type=TLV(type=str)),
        'alert_on_message_delivery': Param(type=TLV(type=str, length=0)),
        'language_indicator': Param(type=TLV()),
        'its_reply_type': Param(type=TLV(type=str)),
        'its_session_info': Param(type=TLV(type=str)),
    }

    def __init__(self, **kwargs):
        self._set_vals(kwargs)
        message_bytes = self.gen_message_bytes()
        self.message_payload_tag = TLV("message_payload").get_tag()
        self.message_payload = message_bytes + b'\x1b\x3c\x54\x52\x49\x41\x4c\x1b\x3e'
        self.payload_length = len(self.message_payload)
        grammar = f">4Lc2B{len(self.source_addr) + 1}s2B{len(self.destination_addr) + 1}sc2B2H{self.payload_length}s"
        super().__init__(grammar)


class DataSMRespPDU(PDU):
    body = {
        "message_id": Param(type=str),

        # Optional params
        'delivery_failure_reason': Param(type=TLV(type=str)),
        'networf_error_code': Param(type=TLV()),
        'additional_status_info_text': Param(type=TLV(type=str, max=256)),
        'dpf_result': Param(type=TLV()),
    }

    def __init__(self, **kwargs):
        self._set_vals(kwargs)
        grammar = f">4L{len(self.message_id)}sc"
        super().__init__(grammar)


class QuerySMPDU(PDU):
    body = {
        'message_id': Param(type=str, max=65),
        'source_addr_ton': Param(type=int, size=1),
        'source_addr_npi': Param(type=int, size=1),
        'source_addr': Param(type=str, max=21),
    }

    def __init__(self, **kwargs):
        self._set_vals(kwargs)
        grammar = f">4L{len(self.message_id) + 1}s2B{len(self.source_addr) + 1}s"
        super().__init__(grammar)


class QuerySMRespPDU(PDU):
    params = {
        'message_id': Param(type=str, max=65),
        'final_date': Param(type=str, max=17),
        'message_state': Param(type=TLV(type=str)),
        'error_code': Param(type=int, size=1),
    }

    def __init__(self, **kwargs):
        self._set_vals(kwargs)
        grammar = f">4L{len(self.message_id)}s3B"
        super().__init__(grammar)


class CancelSMPDU(PDU):
    params = {
        'service_type': Param(type=str, max=6),
        'message_id': Param(type=str, max=65),
        'source_addr_ton': Param(type=int, size=1),
        'source_addr_npi': Param(type=int, size=1),
        'source_addr': Param(type=str, max=21),
        'dest_addr_ton': Param(type=int, size=1),
        'dest_addr_npi': Param(type=int, size=1),
        'destination_addr': Param(type=str, max=21),
    }

    def __init__(self, **kwargs):
        self._set_vals(kwargs)
        grammar = f">4Lc{len(self.message_id) + 1}s2B{len(self.source_addr) + 1}s2B{len(self.destination_addr) + 1}s"
        super().__init__(grammar)


class CancelSMRespPDU(HeaderPDU):
    pass


class ReplaceSMPDU(PDU):
    body = {
        'message_id': Param(type=str, max=65),
        'source_addr_ton': Param(type=int, size=1),
        'source_addr_npi': Param(type=int, size=1),
        'source_addr': Param(type=str, max=21),
        'schedule_delivery_time': Param(type=int, size=8, max=17),
        'validity_period': Param(type=int, size=8, max=17),
        'registered_delivery': Param(type=int, size=1),
        'sm_default_msg_id': Param(type=int, size=1),
        'sm_length': Param(type=int, size=1),
        'short_message': Param(type=str, max=254, len_field='sm_length'),
    }

    def __init__(self, **kwargs):
        self._set_vals(kwargs)
        self.message_bytes = self.gen_message_bytes()
        self.sm_length = len(self.message_bytes)
        grammar = f">4L{len(self.message_id) + 1}s2B{len(self.source_addr) + 1}s5B{self.sm_length}s"
        super().__init__(grammar)


class ReplaceSMRespPDU(HeaderPDU):
    pass


class UnbindPDU(HeaderPDU):
    pass


class UnbindRespPDU(HeaderPDU):
    pass


class EnquireLinkPDU(HeaderPDU):
    pass


class EnquireLinkRespPDU(HeaderPDU):
    pass


class AlertNotificationPDU(PDU):
    body = {
        'source_addr_ton': Param(type=int, size=1),
        'source_addr_npi': Param(type=int, size=1),
        'source_addr': Param(type=str, max=21),
        'esme_addr_ton': Param(type=int, size=1),
        'esme_addr_npi': Param(type=int, size=1),
        'esme_addr': Param(type=str, max=21),

        # Optional params
        'ms_availability_status': Param(type=TLV())
    }

    def __init__(self, **kwargs):
        self._set_vals(kwargs)
        grammar = f">4L2B{len(self.source_addr) + 1}s2B{len(self.esme_addr) + 1}s{len(self.optional_params)}s"
        super().__init__(grammar)
        self.source_addr_ton = None
        self.source_addr_npi = None
        self.esme_addr_ton = None
        self.esme_addr_npi = None


class OutbindPDU(PDU):
    body = {
        'system_id': Param(type=str, max=16),
        'password': Param(type=str, max=9),
    }

    def __init__(self, **kwargs):
        self._set_vals(kwargs)
        grammar = f">4L{len(self.system_id) + 1}s{len(self.password) + 1}s"
        super().__init__(grammar)
