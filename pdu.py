import struct
import gsm0338

import config
import consts
from utils import get_tag


class Param:
    def __init__(self, type, size=None, min=None, max=None, len_field=None):
        self.type = type
        self.size = size
        self.min = min
        self.max = max
        self.len_field = len_field


class PDU:
    header = {
        "command_length": Param(type=int, size=4),
        "command_id": Param(type=int, size=4),
        "command_status": Param(type=int, size=4),
        "sequence_number": Param(type=int, size=4),
    }

    def __init__(self, grammar=">4L"):
        self.struct = struct.Struct(grammar)
        self.command_length = self.struct.size
        self.pack_param = []

    def _set_vals(self, d):
        for k, v in d.items():
            setattr(self, k, v)

    def gen_pack_param(self):
        for k, v in self.header.items():
            param = getattr(self, k)
            self.pack_param.append(param)
        try:
            self.body
        except AttributeError:
            return
        for k, v in self.body.items():
            param = getattr(self, k)
            if v.type == str:
                value = getattr(self, k)
                if type(value) == str:
                    param = value.encode()
                    if k in config.ADD_NULL_PARAMS:
                        param = value.encode() + b'\x00'
                    if k == "short_message":
                        param = self.message_bytes
            self.pack_param.append(param)

    def pack(self):
        self.gen_pack_param()
        data = self.struct.pack(*self.pack_param)
        return data

    def unpack(self, resp):
        return self.struct.unpack(resp)

    def gen_message_bytes(self):
        if self.data_coding == consts.SMPP_ENCODING_ISO10646:
            return self.short_message.encode("utf-16be")
        elif self.data_coding == consts.SMPP_ENCODING_DEFAULT:
            return gsm0338.Codec().encode(self.short_message)[0]

    def __str__(self):
        s = 'PDU('
        for k in self.header:
            s += f"{k}:{getattr(self, k)},"
        try:
            self.body
        except AttributeError:
            pass
        for k in self.body:
            s += f"{k}:{getattr(self, k)},"
        return s + ')'


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
    def __init__(self, **kwargs):
        self._set_vals(kwargs)
        grammar = f">4L{len(self.system_id)}sc"
        super().__init__(grammar)

    def __str__(self):
        return super().__str__() + f"system_id:{self.system_id.decode('ascii')})"


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
        # 'user_message_reference': Param(type=int, size=2),
        # 'source_port': Param(type=int, size=2),
        # 'source_addr_subunit': Param(type=int, size=2),
        # 'destination_port': Param(type=int, size=2),
        # 'dest_addr_subunit': Param(type=int, size=1),
        # 'sar_msg_ref_num': Param(type=int, size=2),
        # 'sar_total_segments': Param(type=int, size=1),
        # 'sar_segment_seqnum': Param(type=int, size=1),
        # 'more_messages_to_send': Param(type=int, size=1),
        # 'payload_type': Param(type=int, size=1),
        # 'message_payload': Param(type=str, max=260),
        # 'privacy_indicator': Param(type=int, size=1),
        # 'callback_num': Param(type=str, min=4, max=19),
        # 'callback_num_pres_ind': Param(type=int, size=1),
        # 'source_subaddress': Param(type=str, min=2, max=23),
        # 'dest_subaddress': Param(type=str, min=2, max=23),
        # 'user_response_code': Param(type=int, size=1),
        # 'display_time': Param(type=int, size=1),
        # 'sms_signal': Param(type=int, size=2),
        # 'ms_validity': Param(type=int, size=1),
        # 'ms_msg_wait_facilities': Param(type=int, size=1),
        # 'number_of_messages': Param(type=int, size=1),
        # 'alert_on_message_delivery': Param(type=str),
        # 'language_indicator': Param(type=int, size=1),
        # 'its_reply_type': Param(type=int, size=1),
        # 'its_session_info': Param(type=int, size=2),
        # 'ussd_service_op': Param(type=int, size=1),
    }

    def __init__(self, **kwargs):
        self._set_vals(kwargs)
        self.message_bytes = self.gen_message_bytes()
        self.sm_length = len(self.message_bytes)
        grammar = f">4L{len(self.service_type)}s2B{len(self.source_addr) + 1}s2B{len(self.destination_addr) + 1}" + \
                  f"s3B2c5B{self.sm_length}s"
        super().__init__(grammar)


class SubmitSMRespPDU(PDU):
    body = {
        "message_id": Param(type=str)
    }

    def __init__(self, **kwargs):
        self._set_vals(kwargs)
        grammar = f">4L{len(self.message_id)}sc"
        super().__init__(grammar)


class DeliverSMPDU(PDU):
    body = {
        "source_addr": Param(type=str),
        "destination_addr": Param(type=str),
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
    }

    def __init__(self, **kwargs):
        self._set_vals(kwargs)
        message_bytes = self.gen_message_bytes()
        self.message_payload_tag = get_tag("message_payload")
        self.message_payload = message_bytes + b'\x1b\x3c\x54\x52\x49\x41\x4c\x1b\x3e'
        self.payload_length = len(self.message_payload)
        grammar = f">4Lc2B{len(self.source_addr) + 1}s2B{len(self.destination_addr) + 1}sc2B2H{self.payload_length}s"
        super().__init__(grammar)

    def gen_pack_param(self):
        super().gen_pack_param()
        self.pack_param.pop()
        self.pack_param.extend([self.message_payload_tag, self.payload_length, self.message_payload])


class DataSMRespPDU(SubmitSMRespPDU):
    pass


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
        'message_state': Param(type=int, size=1),
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
        # 'ms_availability_status': Param(type=int, size=1),
    }

    def __init__(self, **kwargs):
        self._set_vals(kwargs)
        grammar = f">4L2B{len(self.source_addr) + 1}s2B{len(self.esme_addr) + 1}s{len(self.optional_params)}s"
        super().__init__(grammar)
        self.source_addr_ton = None
        self.source_addr_npi = None
        self.esme_addr_ton = None
        self.esme_addr_npi = None
