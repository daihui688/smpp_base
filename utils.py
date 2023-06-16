import os
import netifaces

from pdu import *

interfaces_ips = {}


def get_pdu(command_name):
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
            'outbind': OutbindPDU,
            'unbind': UnbindPDU,
            'unbind_resp': UnbindRespPDU,
            'enquire_link': EnquireLinkPDU,
            'enquire_link_resp': EnquireLinkRespPDU,
            'alert_notification': AlertNotificationPDU,
            'submit_multi': SubmitMultiPDU,
            'submit_multi_resp': SubmitMultiRespPDU
        }[command_name]
    except KeyError:
        raise Exception('Command "%s" is not supported' % command_name)


def get_interfaces_and_ips():
    for iface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(iface)
        if netifaces.AF_INET in addrs:
            ip_address = addrs[netifaces.AF_INET][0]['addr']
            interfaces_ips[iface] = ip_address
    return interfaces_ips


def get_optional_param_name(num):
    for name, v in consts.OPTIONAL_PARAMS.items():
        if v == num:
            return name


def contains_chinese(message):
    for char in message:
        if '\u4e00' <= char <= '\u9fff':
            return True
    return False


def create_dir(dir_str):
    if not os.path.exists(dir_str):
        os.makedirs(dir_str)
