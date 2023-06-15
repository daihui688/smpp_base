EMPTY_STRING = b''
NULL_STRING = b'\0'
NULL_BYTE = b'\x00'


# Message part lengths in different encodings.
# SMPP 3.4, 2.2.1.2
SEVENBIT_LENGTH = 160
EIGHTBIT_LENGTH = 140
UCS2_LENGTH = 70

MULTIPART_HEADER_SIZE = 6

SEVENBIT_PART_SIZE = SEVENBIT_LENGTH - 7  # TODO: where does 7 come from?
EIGHTBIT_PART_SIZE = 140 - MULTIPART_HEADER_SIZE
UCS2_PART_SIZE = 140 - MULTIPART_HEADER_SIZE  # must be an even number anyway


# SMPP error codes.
ESME_ROK = 0x00000000   # 无错误
ESME_RINVMSGLEN = 0x00000001   # 消息长度错
ESME_RINVCMDLEN = 0x00000002   # 命令长度错
ESME_RINVCMDID = 0x00000003   # 无效的命令 ID
ESME_RINVBNDSTS = 0x00000004   # 命令与 Bind 状态不一致
ESME_RALYBND = 0x00000005   # ESME 已经绑定
ESME_RINVPRTFLG = 0x00000006   # 无效的优先标识
ESME_RINVREGDLVFLG = 0x00000007   # 无效状态报告标识
ESME_RSYSERR = 0x00000008   # 系统错
ESME_RINVSRCADR = 0x0000000A   # 源地址无效
ESME_RINVDSTADR = 0x0000000B   # 目标地址错
ESME_RINVMSGID = 0x0000000C   # 消息 ID 错
ESME_RBINDFAIL = 0x0000000D   # 绑定失败
ESME_RINVPASWD = 0x0000000E   # 密码错误
ESME_RINVSYSID = 0x0000000F   # 系统 ID 错误
ESME_RCANCELFAIL = 0x00000011   # Cancel 消息 失败
ESME_RREPLACEFAIL = 0x00000013   # Replace 消息失败
ESME_RMSGQFUL = 0x00000014   # 消息队列满
ESME_RINVSERTYP = 0x00000015   # 服务类型非法
ESME_RINVNUMDESTS = 0x00000033   # 目标号错误
ESME_RINVDLNAME = 0x00000034   # 名字分配表错误
ESME_RINVDESTFLAG = 0x00000040   # 目标标识错误
ESME_RINVSUBREP = 0x00000042   # 无效的'submit with replace'请求(如sumit_sm操作中replace_if_present_flag已设置)
ESME_RINVESMCLASS = 0x00000043   # esm_class 字段数据非法
ESME_RCNTSUBDL = 0x00000044   # 无法提交至分配表
ESME_RSUBMITFAIL = 0x00000045   # submit_sm 或 submit_muli失败
ESME_RINVSRCTON = 0x00000048   # 无效的源地址 TON
ESME_RINVSRCNPI = 0x00000049   # 无效的源地址 NPI
ESME_RINVDSTTON = 0x00000050   # 无效的目标地址 TON
ESME_RINVDSTNPI = 0x00000051   # 无效的目标地址 NPI
ESME_RINVSYSTYP = 0x00000053   # System_type 字段无效
ESME_RINVREPFLAG = 0x00000054   # replace_if_present_flag 字 段无效
ESME_RINVNUMMSGS = 0x00000055   # 消息序号无效
ESME_RTHROTTLED = 0x00000058   # 节流错 ESME 超出消息限制
ESME_RINVSCHED = 0x00000061   # 无效的定时时间
ESME_RINVEXPIRY = 0x00000062   # 无效的超时时间
ESME_RINVDFTMSGID = 0x00000063   # 预定义消息无效或不存在
ESME_RX_T_APPN = 0x00000064   # ESME 接收端暂时出错
ESME_RX_P_APPN = 0x00000065   # ESME 接收端永久出错
ESME_RX_R_APPN = 0x00000066   # ESME 接收端拒绝消息出错
ESME_RQUERYFAIL = 0x00000067   # Query_sm 失败
ESME_RINVOPTPARSTREAM = 0x000000C0   # PDU报体可选部分出错
ESME_VOPTPARNOTALLWD = 0x000000C1   # 可选参数不允许
ESME_RINVPARLEN = 0x000000C2   # 参数长度错
ESME_RMISSINGOPTPARAM = 0x000000C3   # 需要的可选参数丢失
ESME_RINVOPTPARAMVAL = 0x000000C4   # 无效的可选参数值
ESME_RDELIVERYFAILURE = 0x000000FE   # 下发消息失败(用于data_sm_resp)
ESME_RUNKNOWNERR = 0x000000FF   # 不明错误

# Status description strings.
DESCRIPTIONS = {
    ESME_ROK: 'No Error',
    ESME_RINVMSGLEN: 'Message Length is invalid',
    ESME_RINVCMDLEN: 'Command Length is invalid',
    ESME_RINVCMDID: 'Invalid Command ID',
    ESME_RINVBNDSTS: 'Incorrect BIND Status for given command',
    ESME_RALYBND: 'ESME Already in Bound State',
    ESME_RINVPRTFLG: 'Invalid Priority Flag',
    ESME_RINVREGDLVFLG: '<Desc Not Set>',
    ESME_RSYSERR: 'System Error',
    ESME_RINVSRCADR: 'Invalid Source Address',
    ESME_RINVDSTADR: 'Invalid Destination Address',
    ESME_RINVMSGID: 'Invalid Message ID',
    ESME_RBINDFAIL: 'Bind Failed',
    ESME_RINVPASWD: 'Invalid Password',
    ESME_RINVSYSID: 'Invalid System ID',
    ESME_RCANCELFAIL: 'Cancel SM Failed',
    ESME_RREPLACEFAIL: 'Replace SM Failed',
    ESME_RMSGQFUL: 'Message Queue is full',
    ESME_RINVSERTYP: 'Invalid Service Type',
    ESME_RINVNUMDESTS: 'Invalid number of destinations',
    ESME_RINVDLNAME: 'Invalid Distribution List name',
    ESME_RINVDESTFLAG: 'Invalid Destination Flag (submit_multi)',
    ESME_RINVSUBREP: 'Invalid Submit With Replace request (replace_if_present_flag set)',
    ESME_RINVESMCLASS: 'Invalid esm_class field data',
    ESME_RCNTSUBDL: 'Cannot submit to Distribution List',
    ESME_RSUBMITFAIL: 'submit_sm or submit_multi failed',
    ESME_RINVSRCTON: 'Invalid Source address TON',
    ESME_RINVSRCNPI: 'Invalid Source address NPI',
    ESME_RINVDSTTON: 'Invalid Destination address TON',
    ESME_RINVDSTNPI: 'Invalid Destination address NPI',
    ESME_RINVSYSTYP: 'Invalid system_type field',
    ESME_RINVREPFLAG: 'Invalid replace_if_present flag',
    ESME_RINVNUMMSGS: 'Invalid number of messages',
    ESME_RTHROTTLED: 'Throttling error (ESME has exceeded allowed message limits)',
    ESME_RINVSCHED: 'Invalid Scheduled Delivery Time',
    ESME_RINVEXPIRY: 'Invalid message validity period (Expiry Time)',
    ESME_RINVDFTMSGID: 'Predefined Message is invalid or not found',
    ESME_RX_T_APPN: 'ESME received Temporary App Error Code',
    ESME_RX_P_APPN: 'ESME received Permanent App Error Code',
    ESME_RX_R_APPN: 'ESME received Reject Message Error Code',
    ESME_RQUERYFAIL: 'query_sm request failed',
    ESME_RINVOPTPARSTREAM: 'Error in the optional part of the PDU body',
    ESME_VOPTPARNOTALLWD: 'Optional Parameter not allowed',
    ESME_RINVPARLEN: 'Invalid Parameter Length',
    ESME_RMISSINGOPTPARAM: 'Expected Optional Parameter missing',
    ESME_RINVOPTPARAMVAL: 'Invalid Optional Parameter Value',
    ESME_RDELIVERYFAILURE: 'Delivery Failure (used data_sm_resp)',
    ESME_RUNKNOWNERR: 'Unknown Error',
}


# Internal client state.
CLIENT_STATE_CLOSED = 0
CLIENT_STATE_OPEN = 1
CLIENT_STATE_BOUND_TX = 2
CLIENT_STATE_BOUND_RX = 3
CLIENT_STATE_BOUND_TRX = 4


# TON (Type Of Number) values.
TON_UNK = 0x00
TON_INTL = 0x01
TON_NATNL = 0x02
TON_NWSPEC = 0x03
TON_SBSCR = 0x04
TON_ALNUM = 0x05
TON_ABBREV = 0x06


# NPI (Numbering Plan Indicator) values.
NPI_UNK = 0x00  # Unknown
NPI_ISDN = 0x01  # ISDN (E163/E164)
NPI_DATA = 0x03  # Data (X.121)
NPI_TELEX = 0x04  # Telex (F.69)
NPI_LNDMBL = 0x06  # Land Mobile (E.212)
NPI_NATNL = 0x08  # National
NPI_PRVT = 0x09  # Private
NPI_ERMES = 0x0A  # ERMES
NPI_IP = 0x0E  # IPv4
NPI_WAP = 0x12  # WAP

# Service_type
Service_type_NULL = '' # 确省
Service_type_CMT = 'CMT' # 蜂窝式消息
Service_type_CPT = 'CPT' # 蜂窝式寻呼
Service_type_VMN = 'VMN' # 语音信箱通知
Service_type_VMA = 'VMA' # 语音信箱告警
Service_type_WAP = 'WAP' # 无线应用协议
Service_type_USSD = 'USSD' # 服务数据的非结构化实现

# Encoding types.
ENCODING_DEFAULT = 0x00  # SMSC Default
ENCODING_IA5 = 0x01  # IA5 (CCITT T.50)/ASCII (ANSI X3.4)
ENCODING_BINARY = 0x02  # Octet unspecified (8-bit binary)
ENCODING_ISO88591 = 0x03  # Latin 1 (ISO-8859-1)
ENCODING_BINARY2 = 0x04  # Octet unspecified (8-bit binary)
ENCODING_JIS = 0x05  # JIS (X 0208-1990)
ENCODING_ISO88595 = 0x06  # Cyrillic (ISO-8859-5)
ENCODING_ISO88598 = 0x07  # Latin/Hebrew (ISO-8859-8)
ENCODING_ISO10646 = 0x08  # UCS2 (ISO/IEC-10646)
ENCODING_PICTOGRAM = 0x09  # Pictogram Encoding
ENCODING_ISO2022JP = 0x0A  # ISO-2022-JP (Music Codes)
ENCODING_EXTJIS = 0x0D  # Extended Kanji JIS (X 0212-1990)
ENCODING_KSC5601 = 0x0E  # KS C 5601


# Language types.
LANG_DEFAULT = 0x00
LANG_EN = 0x01
LANG_FR = 0x02
LANG_ES = 0x03
LANG_DE = 0x04


# ESM class values.
MSGMODE_DEFAULT = 0x00  # Default SMSC mode (e.g. Store and Forward)
MSGMODE_DATAGRAM = 0x01  # Datagram mode
MSGMODE_FORWARD = 0x02  # Forward (i.e. Transaction) mode
MSGMODE_STOREFORWARD = 0x03  # Explicit Store and Forward mode


MSGTYPE_DEFAULT = 0x00  # Default message type (i.e. normal message)
MSGTYPE_DELIVERYACK = 0x08  # Message containts ESME Delivery acknowledgement
MSGTYPE_USERACK = 0x10  # Message containts ESME Manual/User acknowledgement


GSMFEAT_NONE = 0x00  # No specific features selected
GSMFEAT_UDHI = 0x40  # UDHI Indicator (only relevant for MT msgs)
GSMFEAT_REPLYPATH = 0x80  # Set Reply Path (only relevant for GSM net)
GSMFEAT_UDHIREPLYPATH = 0xC0  # Set UDHI and Reply Path (for GSM net)


# SMPP Protocol ID.
PID_DEFAULT = 0x00  # Default
PID_RIP = 0x41  # Replace if present on handset


# SMPP User Data Header Information Element Identifier.
UDHIEIE_CONCATENATED = 0x00  # Concatenated short message, 8-bit ref
UDHIEIE_SPECIAL = 0x01
UDHIEIE_RESERVED = 0x02
UDHIEIE_PORT8 = 0x04
UDHIEIE_PORT16 = 0x05
UDHIEIE_CONCATENATED16 = 0x08


# `ms_availability_status` parameter from `alert_notification` operation.
MS_AVAILABILITY_STATUS_AVAILABLE = 0x00
MS_AVAILABILITY_STATUS_DENIED = 0x01
MS_AVAILABILITY_STATUS_UNAVAILABLE = 0x02


# `registered_delivery` parameter used to request an SMSC delivery receipt and/or SME originated acknowledgements.
# SMSC Delivery Receipt (bits 1 and 0).
SMSC_DELIVERY_RECEIPT_NONE = 0x00  # No SMSC Delivery Receipt requested (default)
SMSC_DELIVERY_RECEIPT_BOTH = 0x01  # SMSC Delivery Receipt requested where final delivery outcome is delivery success or failure
SMSC_DELIVERY_RECEIPT_FAILURE = 0x02  # SMSC Delivery Receipt requested where the final delivery outcome is delivery failure
SMSC_DELIVERY_RECEIPT_BITMASK = 0x03  # Reserved.


# SME originated Acknowledgement (bits 3 and 2).
SME_ACK_BITMASK = 0x0C  # No recipient SME acknowledgment requested (default)
SME_ACK_NONE = 0x00  # No recipient SME acknowledgment requested (default)
SME_ACK_DELIVERY = 0x04  # SME Delivery Acknowledgement requested
SME_ACK_MANUAL = 0x08  # SME Manual/User Acknowledgment requested
SME_ACK_BOTH = 0x0C  # Both Delivery and Manual/User Acknowledgment requested


# Intermediate Notification (bit 5).
INT_NOTIFICATION_BITMASK = 0x10
INT_NOTIFICATION_NONE = 0x00  # No Intermediate notification requested (default)
INT_NOTIFICATION_REQUESTED = 0x10  # Intermediate notification requested


# SMPP protocol versions.
VERSION_33 = 0x33
VERSION_34 = 0x34


# Network types.
NETWORK_TYPE_UNKNOWN = 0x00
NETWORK_TYPE_GSM = 0x01
NETWORK_TYPE_TDMA = 0x02
NETWORK_TYPE_CDMA = 0x03
NETWORK_TYPE_PDC = 0x04
NETWORK_TYPE_PHS = 0x05
NETWORK_TYPE_IDEN = 0x06
NETWORK_TYPE_AMPS = 0x07
NETWORK_TYPE_PAGING = 0x08


# Message state.
MESSAGE_STATE_ENROUTE = 1 # 消息正在传输
MESSAGE_STATE_DELIVERED = 2 # 消息已送达
MESSAGE_STATE_EXPIRED = 3 # 消息超时
MESSAGE_STATE_DELETED = 4 # 消息被删除
MESSAGE_STATE_UNDELIVERABLE = 5 # 消息不可送达
MESSAGE_STATE_ACCEPTED = 6 # 消息已接收(如已被客服代表用户手工读取)
MESSAGE_STATE_UNKNOWN = 7 # 消息状态无效
MESSAGE_STATE_REJECTED = 8 # 消息被拒绝


COMMAND_STATES = {
    'bind_transmitter': (CLIENT_STATE_OPEN,),
    'bind_transmitter_resp': (CLIENT_STATE_OPEN,),
    'bind_receiver': (CLIENT_STATE_OPEN,),
    'bind_receiver_resp': (CLIENT_STATE_OPEN,),
    'bind_transceiver': (CLIENT_STATE_OPEN,),
    'bind_transceiver_resp': (CLIENT_STATE_OPEN,),
    'outbind': (CLIENT_STATE_OPEN,),
    'unbind': (
        CLIENT_STATE_BOUND_TX,
        CLIENT_STATE_BOUND_RX,
        CLIENT_STATE_BOUND_TRX,
    ),
    'unbind_resp': (
        CLIENT_STATE_BOUND_TX,
        CLIENT_STATE_BOUND_RX,
        CLIENT_STATE_BOUND_TRX,
    ),
    'submit_sm': (CLIENT_STATE_BOUND_TX, CLIENT_STATE_BOUND_TRX),
    'submit_sm_resp': (CLIENT_STATE_BOUND_TX, CLIENT_STATE_BOUND_TRX),
    'submit_sm_multi': (CLIENT_STATE_BOUND_TX, CLIENT_STATE_BOUND_TRX),
    'submit_sm_multi_resp': (CLIENT_STATE_BOUND_TX, CLIENT_STATE_BOUND_TRX),
    'data_sm': (
        CLIENT_STATE_BOUND_TX,
        CLIENT_STATE_BOUND_RX,
        CLIENT_STATE_BOUND_TRX,
    ),
    'data_sm_resp': (
        CLIENT_STATE_BOUND_TX,
        CLIENT_STATE_BOUND_RX,
        CLIENT_STATE_BOUND_TRX,
    ),
    'deliver_sm': (CLIENT_STATE_BOUND_RX, CLIENT_STATE_BOUND_TRX),
    'deliver_sm_resp': (CLIENT_STATE_BOUND_RX, CLIENT_STATE_BOUND_TRX),
    'query_sm': (CLIENT_STATE_BOUND_RX, CLIENT_STATE_BOUND_TRX),
    'query_sm_resp': (CLIENT_STATE_BOUND_RX, CLIENT_STATE_BOUND_TRX),
    'cancel_sm': (CLIENT_STATE_BOUND_RX, CLIENT_STATE_BOUND_TRX,),
    'cancel_sm_resp': (CLIENT_STATE_BOUND_RX, CLIENT_STATE_BOUND_TRX,),
    'replace_sm': (CLIENT_STATE_BOUND_TX,),
    'replace_sm_resp': (CLIENT_STATE_BOUND_TX,),
    'enquire_link': (
        CLIENT_STATE_BOUND_TX,
        CLIENT_STATE_BOUND_RX,
        CLIENT_STATE_BOUND_TRX,
    ),
    'enquire_link_resp': (
        CLIENT_STATE_BOUND_TX,
        CLIENT_STATE_BOUND_RX,
        CLIENT_STATE_BOUND_TRX,
    ),
    'alert_notification': (CLIENT_STATE_BOUND_RX, CLIENT_STATE_BOUND_TRX),
    'generic_nack': (
        CLIENT_STATE_BOUND_TX,
        CLIENT_STATE_BOUND_RX,
        CLIENT_STATE_BOUND_TRX,
    )
}


STATE_SETTERS = {
    'bind_transmitter_resp': CLIENT_STATE_BOUND_TX,
    'bind_receiver_resp': CLIENT_STATE_BOUND_RX,
    'bind_transceiver_resp': CLIENT_STATE_BOUND_TRX,
    'unbind_resp': CLIENT_STATE_OPEN,
}


OPTIONAL_PARAMS = {
    "dest_addr_subunit": 0x0005,
    "dest_network_type": 0x0006,
    "dest_bearer_type": 0x0007,
    "dest_telematics_id": 0x0008,
    "source_addr_subunit": 0x000D,
    "source_network_type": 0x000E,
    "source_bearer_type": 0x000F,
    "source_telematics_id": 0x0010,
    "qos_time_to_live": 0x0017,
    "payload_type": 0x0019,
    "additional_status_info_text": 0x001D,
    "receipted_message_id": 0x001E,
    "ms_msg_wait_facilities": 0x0030,
    "privacy_indicator": 0x0201,
    "source_subaddress": 0x0202,
    "dest_subaddress": 0x0203,
    "user_message_reference": 0x0204,
    "user_response_code": 0x0205,
    "source_port": 0x020A,
    "destination_port": 0x020B,
    "sar_msg_ref_num": 0x020C,
    "language_indicator": 0x020D,
    "sar_total_segments": 0x020E,
    "sar_segment_seqnum": 0x020F,
    "sc_interface_version": 0x0210,
    "callback_num_pres_ind": 0x0302,
    "callback_num_atag": 0x0303,
    "number_of_messages": 0x0304,
    "callback_num": 0x0381,
    "dpf_result": 0x0420,
    "set_dpf": 0x0421,
    "ms_availability_status": 0x0422,
    "network_error_code": 0x0423,
    "message_payload": 0x0424,
    "delivery_failure_reason": 0x0425,
    "more_messages_to_send": 0x0426,
    "message_state": 0x0427,
    "ussd_service_op": 0x0501,
    "display_time": 0x1201,
    "sms_signal": 0x1203,
    "ms_validity": 0x1204,
    "alert_on_message_delivery": 0x130C,
    "its_reply_type": 0x1380,
    "its_session_info": 0x1383
}


# Integer value struct formats for different sizes.
INT_PACK_FORMATS = {
    1: 'B',
    2: 'H',
    4: 'L',
    8: 'Q'
}
