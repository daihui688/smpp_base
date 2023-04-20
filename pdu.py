class PDU:
    def __init__(self, command_id, command_status, sequence_number, command_params=None):
        self.command_id = command_id
        self.command_status = command_status
        self.sequence_number = sequence_number
        self.command_params = command_params if command_params is not None else {}

    def __str__(self):
        return f"PDU(command_id={self.command_id}, command_status={self.command_status}, sequence_number={self.sequence_number}, command_params={self.command_params})"

    def to_bytes(self):
        # 用于将 PDU 对象转换为字节流以便进行传输
        pass

    @classmethod
    def from_bytes(cls, data):
        # 用于将接收到的字节流转换回 PDU 对象
        pass

    def add_command_param(self, param_name, param_value):
        self.command_params[param_name] = param_value

    def get_command_param(self, param_name):
        return self.command_params.get(param_name, None)
