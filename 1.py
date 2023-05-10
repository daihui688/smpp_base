import time

from smpplib import client, consts

# 连接到SMSC
host = '127.0.0.1'
port = 7777
username = 'login'
password = '123'

client = client.Client(host, port)
client.connect()
client.bind_transceiver(system_id=username, password=password)

# 构建要发送的短消息
source_addr = '18720198878'
destination_addr = '18279230916'
message_text = b'Hello, World!'

# 发送短消息
client.send_message(
    source_addr_ton=consts.SMPP_TON_INTL,
    source_addr_npi=consts.SMPP_NPI_ISDN,
    source_addr=source_addr,
    destination_addr_ton=consts.SMPP_TON_INTL,
    destination_addr_npi=consts.SMPP_NPI_ISDN,
    destination_addr=destination_addr,
    short_message=message_text,
)
time.sleep(1)
# 获取 submit_sm_resp 的响应
resp = client.read_pdu()

message_id = resp.params['message_id']
print('Message ID:', message_id)
client.query_message(message_id=message_id, source_addr_ton=consts.SMPP_TON_INTL,
                     source_addr_npi=consts.SMPP_NPI_ISDN,
                     source_addr=source_addr)


time.sleep(1)
# 断开与SMSC的连接
client.unbind()
client.disconnect()
