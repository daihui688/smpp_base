SMPP_SERVER_HOST = "127.0.0.1"
SMPP_SERVER_PORT = 2775
SOURCE_ADDR = "MySMSService"
DESTINATION_ADDR = "MySMSSClient"
ESME_ADDR = "18279230916"
FUZZ_NUM = 1
SYSTEM_ID = "dh"
PASSWORD = "123"
FUZZ_COMMAND = ["bind_transceiver","submit_sm","deliver_sm_resp","unbind","enquire_link"]
ADD_NULL_PARAMS = ["system_id","password","system_type","source_addr","destination_addr","message_id"]


