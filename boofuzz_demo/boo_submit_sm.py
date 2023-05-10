from boofuzz import *


def boo_submit_sm():
    session = Session(
        target=Target(
            connection=TCPSocketConnection("127.0.0.1", 7777)
        ),
    )

    s_initialize("SMPP_submit_sm")

    # Command length (placeholder, will be automatically calculated)
    s_size("SMPP_Message", length=4, endian=">")
    s_static(b"\x00\x00\x00\x04")  # command_id for submit_sm
    s_static(b"\x00\x00\x00\x00")  # command_status
    s_static(b"\x00\x00\x00\x01")  # sequence_number

    if s_block_start("SMPP_Message"):
        s_string("service_type", fuzzable=True)  # Service type
        s_delim(b"\x00")  # NULL byte delimiter

        s_byte(0x00, name="source_addr_ton", fuzzable=True)  # Source address TON
        s_byte(0x00, name="source_addr_npi", fuzzable=True)  # Source address NPI
        s_string("source_addr", fuzzable=True)  # Source address
        s_delim(b"\x00")  # NULL byte delimiter

        s_byte(0x00, name="dest_addr_ton", fuzzable=True)  # Destination address TON
        s_byte(0x00, name="dest_addr_npi", fuzzable=True)  # Destination address NPI
        s_string("destination_addr", fuzzable=True)  # Destination address
        s_delim(b"\x00")  # NULL byte delimiter

        s_byte(0x00, name="esm_class", fuzzable=True)  # ESM class
        s_byte(0x00, name="protocol_id", fuzzable=True)  # Protocol ID
        s_byte(0x00, name="priority_flag", fuzzable=True)  # Priority flag

        s_string("", fuzzable=True)  # Schedule delivery time
        s_delim(b"\x00")  # NULL byte delimiter

        s_string("", fuzzable=True)  # Validity period
        s_delim(b"\x00")  # NULL byte delimiter

        s_byte(0x00, name="registered_delivery", fuzzable=True)  # Registered delivery
        s_byte(0x00, name="replace_if_present_flag", fuzzable=True)  # Replace if present flag
        s_byte(0x00, name="data_coding", fuzzable=True)  # Data coding
        s_byte(0x00, name="sm_default_msg_id", fuzzable=True)  # SM default message ID

        # Short message length
        s_size("short_message_block", length=1, endian=">", fuzzable=True)

        if s_block_start("short_message_block"):
            s_string("short_message", fuzzable=True)  # Short message
        s_block_end("short_message_block")

    s_block_end("SMPP_Message")

    session.connect(s_get("SMPP_submit_sm"))
    session.fuzz()


if __name__ == "__main__":
    boo_submit_sm()
