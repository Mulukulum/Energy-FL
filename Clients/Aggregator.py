class Aggregator:
    def __init__(self, ip: str, username: str, flwrPort: int, zmqPort: int) -> None:
        self.ip = ip
        self.username = username
        self.flwrPort = flwrPort
        self.zmqPort = zmqPort

    def __repr__(self) -> str:
        return f"""Aggregator {self.username}@{self.ip} hosting flwr on {self.flwrPort} and broadcasting on {self.zmqPort}"""
