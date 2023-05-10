from boofuzz import *


def boo_bind_transceiver():
    # 创建一个会话（Session）对象，设置连接目标为 127.0.0.1:7777
    session = Session(
        target=Target(
            connection=TCPSocketConnection("127.0.0.1", 7777)
        ),
    )

    # 初始化名为 SMPP_bind_transceiver 的请求
    s_initialize("SMPP_bind_transceiver")

    # 开始定义名为 SMPP_Message 的数据块
    if s_block_start("SMPP_Message"):
        # 定义整个 SMPP 消息的长度（占位符，运行时将自动计算）
        s_size("SMPP_Message", length=4, endian=">", inclusive=True)
        # 定义 bind_transceiver 方法的 command_id
        s_static(b"\x00\x00\x00\x09")
        # 定义 command_status
        s_static(b"\x00\x00\x00\x00")
        # 定义 sequence_number
        s_static(b"\x00\x00\x00\x01")

        # 定义 System ID 字段，并设置为可模糊化
        s_string("system_id", fuzzable=True)
        # 定义 NULL 字节分隔符
        s_delim(b"\x00")
        # 定义 Password 字段，并设置为可模糊化
        s_string("password", fuzzable=True)
        # 定义 NULL 字节分隔符
        s_delim(b"\x00")
        # 定义 NULL 字节分隔符
        s_delim(b"\x00")
        # 定义 Interface Version 字段，并设置为可模糊化
        s_byte(0x34, name="interface_version", fuzzable=True)
        # 定义 Address TON 字段，并设置为可模糊化
        s_byte(0x05, name="addr_ton", fuzzable=True)
        # 定义 Address NPI 字段，并设置为可模糊化
        s_byte(0x00, name="addr_npi", fuzzable=True)
        # 定义 NULL 字节分隔符
        s_delim(b"\x00")
    # 结束定义 SMPP_Message 数据块
    s_block_end("SMPP_Message")

    # 将定义的请求（SMPP_bind_transceiver）添加到会话中
    session.connect(s_get("SMPP_bind_transceiver"))

    # 开始模糊测试
    session.fuzz()


if __name__ == "__main__":
    boo_bind_transceiver()
