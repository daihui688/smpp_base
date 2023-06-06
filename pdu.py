import struct
import gsm0338

import consts
import command
from utils import get_tag


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
    def __init__(self, grammar=">LLLL"):
        self.struct = struct.Struct(grammar)
        self.command_length = self.struct.size

    def _set_vals(self, d):
        for k, v in d.items():
            setattr(self, k, v)

    def pack(self):
        data = self.struct.pack(self.command_length, self.command_id, self.command_status, self.sequence_number)
        return data

    def unpack(self, resp):
        return self.struct.unpack(resp)

    def gen_message_bytes(self):
        if self.data_coding == consts.SMPP_ENCODING_ISO10646:
            return self.short_message.encode("utf-16be")
        elif self.data_coding == consts.SMPP_ENCODING_DEFAULT:
            return gsm0338.Codec().encode(self.short_message)[0]

    def __str__(self):
        return f"PDU(command_length:{self.command_length},operation:{command.get_command_name(self.command_id)}," + \
            f"command_status:'{consts.DESCRIPTIONS.get(self.command_status)}',sequence_number:{self.sequence_number}),"


class Param:
    def __init__(self, type, size=None, min=None, max=None, len_field=None):
        self.type = type
        self.size = size
        self.min = min
        self.max = max
        self.len_field = len_field


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
        grammar = f">LLLL{len(self.system_id) + 1}s{len(self.password) + 1}s{len(self.system_type)+1}sBBBc"
        super().__init__(grammar)

    def pack(self):
        data = self.struct.pack(self.command_length, self.command_id, self.command_status, self.sequence_number,
                                self.system_id.encode() + b'\x00', self.password.encode() + b'\x00',
                                self.system_type.encode()+ b'\x00', self.interface_version, self.addr_ton, self.addr_npi,
                                self.address_range)
        return data


class BindTransmitterRespPDU(PDU):
    def __init__(self, **kwargs):
        self._set_vals(kwargs)
        grammar = f">LLLL{len(self.system_id)}sc"
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

    def __init__(self, **kwargs):
        self._set_vals(kwargs)
        self.message_bytes = self.gen_message_bytes()
        self.sm_length = len(self.message_bytes)
        grammar = f">LLLL{len(self.service_type)}sBB{len(self.source_addr) + 1}sBB{len(self.destination_addr) + 1}" + \
                  f"sBBBccBBBBB{self.sm_length}s"
        super().__init__(grammar)

    def pack(self):
        data = self.struct.pack(self.command_length, self.command_id, self.command_status, self.sequence_number,
                                self.service_type, self.source_addr_ton, self.source_addr_npi,
                                self.source_addr.encode() + b'\x00', self.dest_addr_ton, self.dest_addr_npi,
                                self.destination_addr.encode() + b'\x00', self.esm_class, self.protocol_id,
                                self.priority_flag, self.schedule_delivery_time, self.validity_period,
                                self.registered_delivery, self.replace_if_present_flag,
                                self.data_coding, self.sm_default_msg_id, self.sm_length, self.message_bytes)
        return data


class SubmitSMRespPDU(PDU):
    def __init__(self, **kwargs):
        self._set_vals(kwargs)
        grammar = f">LLLL{len(self.message_id)}sc"
        super().__init__(grammar)

    def __str__(self):
        return super().__str__() + f"message_id:{self.message_id})"


class DeliverSMPDU(PDU):
    def __init__(self, **kwargs):
        self._set_vals(kwargs)
        grammar = f">LLLLBBB{len(self.source_addr) + 1}sBB{len(self.destination_addr) + 1}scBcccBcBcB{self.sm_length}s"\
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

    def __str__(self):
        return super().__str__()[:-1] + f",source_addr={self.source_addr},destination_addr={self.destination_addr}"


class DeliverSMRespPDU(PDU):
    def __init__(self, **kwargs):
        self._set_vals(kwargs)
        grammar = f">LLLLc"
        super().__init__(grammar)
        self.message_id = consts.NULL_BYTE

    def pack(self):
        data = self.struct.pack(self.command_length, self.command_id, self.command_status, self.sequence_number,
                                self.message_id)
        return data


class DataSMPDU(PDU):
    def __init__(self, **kwargs):
        self._set_vals(kwargs)
        message_bytes = self.gen_message_bytes()
        self.message_payload_tag = get_tag("message_payload")
        self.message_payload = message_bytes + b'\x1b\x3c\x54\x52\x49\x41\x4c\x1b\x3e'
        self.payload_length = len(self.message_payload)
        grammar = f">LLLLcBB{len(self.source_addr) + 1}sBB{len(self.destination_addr) + 1}scBBHH{self.payload_length}s"
        super().__init__(grammar)

    def pack(self):
        data = self.struct.pack(self.command_length, self.command_id, self.command_status, self.sequence_number,
                                self.service_type, self.source_addr_ton, self.source_addr_npi,
                                self.source_addr.encode() + b'\x00', self.dest_addr_ton, self.dest_addr_npi,
                                self.destination_addr.encode() + b'\x00', self.esm_class, self.registered_delivery,
                                self.data_coding, self.message_payload_tag, self.payload_length, self.message_payload)
        return data


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
        grammar = f">LLLL{len(self.message_id) + 1}sBB{len(self.source_addr) + 1}s"
        super().__init__(grammar)

    def pack(self):
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

    def __init__(self, **kwargs):
        self._set_vals(kwargs)
        grammar = f">LLLL{len(self.message_id)}sBBB"
        super().__init__(grammar)

    def __str__(self):
        return super().__str__() + f"message_id:{self.message_id}),final_date:{self.final_date}," + \
            f"message_state:{self.message_state},error_code:{self.error_code}"


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
        grammar = f">LLLLc{len(self.message_id) + 1}sBB{len(self.source_addr) + 1}sBB{len(self.destination_addr) + 1}s"
        super().__init__(grammar)

    def pack(self):
        data = self.struct.pack(self.command_length, self.command_id, self.command_status, self.sequence_number,
                                self.service_type, self.message_id.encode() + b'\x00',
                                self.source_addr_ton, self.source_addr_npi, self.source_addr.encode() + b'\x00',
                                self.dest_addr_ton, self.dest_addr_npi, self.destination_addr.encode() + b'\x00')
        return data


class CancelSMRespPDU(PDU):
    def __init__(self, **kwargs):
        self._set_vals(kwargs)
        super().__init__()


class ReplaceSMPDU(PDU):
    body = {
        'message_id': Param(type=str, max=65),
        'source_addr_ton': Param(type=int, size=1),
        'source_addr_npi': Param(type=int, size=1),
        'source_addr': Param(type=str, max=21),
        'schedule_delivery_time': Param(type=int, max=17),
        'validity_period': Param(type=int, max=17),
        'registered_delivery': Param(type=int, size=1),
        'sm_default_msg_id': Param(type=int, size=1),
        'sm_length': Param(type=int, size=1),
        'short_message': Param(type=str, max=254, len_field='sm_length'),
    }

    def __init__(self, **kwargs):
        self._set_vals(kwargs)
        self.message_bytes = self.gen_message_bytes()
        self.sm_length = len(self.message_bytes)
        grammar = f">LLLL{len(self.message_id) + 1}sBB{len(self.source_addr) + 1}sBBBBB{self.sm_length}s"
        super().__init__(grammar)

    def pack(self):
        data = self.struct.pack(self.command_length, self.command_id, self.command_status, self.sequence_number,
                                self.message_id.encode() + b'\x00', self.source_addr_ton, self.source_addr_npi,
                                self.source_addr.encode() + b'\x00', self.schedule_delivery_time, self.validity_period,
                                self.registered_delivery, self.sm_default_msg_id, self.sm_length, self.message_bytes)
        return data


class ReplaceSMRespPDU(PDU):
    def __init__(self, **kwargs):
        self._set_vals(kwargs)
        super().__init__()


class UnbindPDU(PDU):
    def __init__(self, **kwargs):
        self._set_vals(kwargs)
        super().__init__()


class UnbindRespPDU(PDU):
    def __init__(self, **kwargs):
        self._set_vals(kwargs)
        super().__init__()


class EnquireLinkPDU(PDU):
    def __init__(self, **kwargs):
        self._set_vals(kwargs)
        super().__init__()


class EnquireLinkRespPDU(PDU):
    def __init__(self, **kwargs):
        self._set_vals(kwargs)
        super().__init__()


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

    def __init__(self, **kwargs):
        self._set_vals(kwargs)
        grammar = f">LLLLBB{len(self.source_addr) + 1}sBB{len(self.esme_addr) + 1}s{len(self.optional_params)}s"
        super().__init__(grammar)
        self.source_addr_ton = None
        self.source_addr_npi = None
        self.esme_addr_ton = None
        self.esme_addr_npi = None

    def __str__(self):
        return super().__str__() + f"source_addr={self.source_addr},esme_addr={self.esme_addr})"
