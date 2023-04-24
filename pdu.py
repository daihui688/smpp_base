import struct
import consts
import command_types
import gsm0338


def factory(command_name, **kwargs):
    """Return instance of a specific command class"""

    try:
        return {
            # 'bind_transmitter': BindTransmitter,
            # 'bind_transmitter_resp': BindTransmitterResp,
            # 'bind_receiver': BindReceiver,
            # 'bind_receiver_resp': BindReceiverResp,
            'bind_transceiver': BindTransceiverPDU,
            'bind_transceiver_resp': BindTransceiverRespPDU,
            # 'data_sm': DataSM,
            # 'data_sm_resp': DataSMResp,
            # 'generic_nack': GenericNAck,
            'submit_sm': SubmitSMPDU,
            'submit_sm_resp': SubmitSMRespPDU,
            'deliver_sm': DeliverSMPDU,
            'deliver_sm_resp': DeliverSMRespPDU,
            # 'query_sm': QuerySM,
            # 'query_sm_resp': QuerySMResp,
            'unbind': UnbindPDU,
            'unbind_resp': UnbindRespPDU,
            'enquire_link': EnquireLinkPDU,
            'enquire_link_resp': EnquireLinkRespPDU,
            # 'alert_notification': AlertNotification,
        }[command_name]
    except KeyError:
        raise Exception('Command "%s" is not supported' % command_name)


class PDU:
    def __init__(self, command_id, result, sequence_number, command_params=None):
        self.command_id = command_id  # Operation
        self.result = result
        self.sequence_number = sequence_number
        self.struct = struct.Struct(">LLLL")
        self.length = None
        self.command_params = command_params if command_params is not None else {}

    def __str__(self):
        return f"PDU(length={self.struct.size},operation={command_types.get_command_name(self.command_id)},result={self.result} sequence_number={self.sequence_number})"

    def pack(self):
        data = self.struct.pack(self.struct.size, self.command_id, self.result, self.sequence_number)
        return data

    def unpack(self, resp):
        return self.struct.unpack(resp)

    def add_command_param(self, param_name, param_value):
        self.command_params[param_name] = param_value

    def get_command_param(self, param_name):
        return self.command_params.get(param_name, None)


class Params():
    def __init__(self, type, max):
        self.type = type
        self.max = max


class BindTransceiverPDU(PDU):
    def __init__(self, command_id, result, sequence_number, system_id, password):
        super().__init__(command_id, result, sequence_number)
        self.system_id = system_id
        self.password = password if len(password) < 9 else password[:8]
        self.struct = struct.Struct(f">LLLL{len(self.system_id) + 1}s{len(self.password) + 1}s5s")

    def pack(self):
        data = self.struct.pack(self.struct.size, self.command_id, self.result, self.sequence_number,
                                self.system_id.encode() + b'\x00', self.password.encode() + b'\x00',
                                b'\x00\x34\x00\x00\x00')
        return data


class BindTransceiverRespPDU(PDU):
    def __init__(self, command_id=None, result=None, sequence_number=None, system_id=None):
        super().__init__(command_id, result, sequence_number)
        self.system_id = system_id
        self.struct = struct.Struct(f">LLLL{len(self.system_id)}sc")

    def __str__(self):
        return f"PDU(length={self.struct.size}, operation={command_types.get_command_name(self.command_id)}, result={self.result}, sequence_number={self.sequence_number}, system_id={self.system_id.decode('ascii')})"


class SubmitSMPDU(PDU):
    def __init__(self, command_id, result, sequence_number, source_addr, destination_addr, data_coding,
                 message):
        super().__init__(command_id, result, sequence_number)
        self.source_addr = source_addr
        self.destination_addr = destination_addr
        self.data_coding = data_coding
        self.message = message
        self.message_bytes = None
        self.struct = struct.Struct(
            f">LLLL3s{len(self.source_addr) + 1}sH{len(self.destination_addr) + 1}sL3sBBB{len(self.message)}s")

    def pack(self):
        if self.data_coding == consts.SMPP_ENCODING_ISO10646:
            self.message_bytes = self.message.encode("utf-16be")
        elif self.data_coding == consts.SMPP_ENCODING_DEFAULT:
            encoder = gsm0338.Codec()
            self.message_bytes = encoder.encode(self.message)[0]

        data = self.struct.pack(self.struct.size, self.command_id, self.result, self.sequence_number,
                                b'\x00\x01\x01', self.source_addr.encode() + b'\x00', 0x0101,
                                self.destination_addr.encode() + b'\x00', 0,
                                b'\x00\x01\x00', self.data_coding, 0, len(self.message_bytes), self.message_bytes)
        return data


class SubmitSMRespPDU(PDU):
    def __init__(self, command_id=None, result=None, sequence_number=None, message_id=None):
        super().__init__(command_id, result, sequence_number)
        self.message_id = message_id
        self.struct = struct.Struct(f">LLLL{len(self.message_id)}sc")

    def __str__(self):
        return f"PDU(length={self.struct.size}, operation={command_types.get_command_name(self.command_id)}, result={self.result}, sequence_number={self.sequence_number}, message_id={self.message_id.decode('ascii')})"


class DeliverSMPDU(PDU):
    def __init__(self, command_id=None, result=None, sequence_number=None, source_addr=None, destination_addr=None,
                 data_coding=None,
                 message=None):
        super().__init__(command_id, result, sequence_number)
        self.source_addr = source_addr
        self.destination_addr = destination_addr
        self.data_coding = data_coding
        self.message = message
        self.message_bytes = None
        self.struct = struct.Struct(
            f">LLLL3s{len(self.source_addr) + 1}sH{len(self.destination_addr) + 1}sL3sBBB{len(self.message)}s")

    def __str__(self):
        return super().__str__()[
               :-1] + f",source_addr={self.source_addr},destination_addr={self.destination_addr},data_coding={self.data_coding})"


class DeliverSMRespPDU(PDU):
    def __init__(self, command_id, result, sequence_number):
        super().__init__(command_id, result, sequence_number)
        self.struct = struct.Struct(f">LLLLc")

    def pack(self):
        data = self.struct.pack(self.struct.size, self.command_id, self.result, self.sequence_number, b'\x00')
        return data


class UnbindPDU(PDU):
    pass


class UnbindRespPDU(PDU):
    def __init__(self, command_id=None, result=None, sequence_number=None):
        super().__init__(command_id, result, sequence_number)


class EnquireLinkPDU(PDU):
    pass


class EnquireLinkRespPDU(PDU):
    def __init__(self, command_id=None, result=None, sequence_number=None):
        super().__init__(command_id, result, sequence_number)
