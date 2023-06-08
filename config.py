SMPP_SERVER_HOST = "127.0.0.1"
SMPP_SERVER_PORT = 7777
SOURCE_ADDR = "MySMSService"
DESTINATION_ADDR = "MySMSSClient"
ESME_ADDR = "8618279230916"
FUZZ_NUM = 1
SYSTEM_ID = "login"
PASSWORD = "12345"
FUZZ_COMMAND = ["bind_transceiver","submit_sm","deliver_sm_resp","query_sm",
                "cancel_sm","replace_sm","unbind","enquire_link"]


