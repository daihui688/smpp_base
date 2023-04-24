# data = "jj刚刚好".encode("utf-16be")
# print(data,len(data))
# import gsm0338
# encoder = gsm0338.Codec()
# print(encoder.encode("jjss")[0])
# print("jjss".encode())

import smpplib.client
import smpplib.gsm
import smpplib.consts

# Replace these values with the ones provided by your SMS gateway provider
SMSC_IP = 'localhost'
SMSC_PORT = 7778
SYSTEM_ID = 'login'
PASSWORD = '12345'

# Your own phone number
MY_PHONE_NUMBER = '+8618279230916'
MESSAGE = 'Hello, this is a test message.'

# Create an SMPP client
client = smpplib.client.Client(SMSC_IP, SMSC_PORT)

# Bind the client to the SMSC
client.bind_transceiver(system_id=SYSTEM_ID, password=PASSWORD)

# Send the message
client.send_message(
    source_addr_ton=smpplib.consts.SMPP_TON_INTL,
    source_addr_npi=smpplib.consts.SMPP_NPI_ISDN,
    source_addr='YourBrand',
    dest_addr_ton=smpplib.consts.SMPP_TON_INTL,
    dest_addr_npi=smpplib.consts.SMPP_NPI_ISDN,
    destination_addr=MY_PHONE_NUMBER,
    short_message=MESSAGE,
    data_coding=smpplib.consts.SMPP_ENCODING_DEFAULT,
    esm_class=smpplib.consts.SMPP_MSGMODE_DEFAULT,
    registered_delivery=True,
)

# Close the connection
client.unbind()
client.disconnect()


