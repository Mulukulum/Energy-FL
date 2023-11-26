

class Aggregator:
    
    def __init__(self, ip: str, username: str, flwrPort: int, zmqPort: int) -> None:
        self.ip = ip
        self.username = username
        self.flwrPort = flwrPort
        self.zmqPort = zmqPort


    def __repr__(self) -> str:
        return f"""Aggregator {self.username}@{self.ip} hosting flwr on {self.flwrPort} and broadcasting on {self.zmqPort}"""

    def ZMQ_setup(self):
        import zmq

        self.context = zmq.Context()
        self.broadcast = self.context.socket(zmq.PUB)
        self.broadcast.bind(f"tcp://{self.ip}:{self.zmqPort}")

    def ZMQ_stop_power_collection(self):
        from common import configuration
        self.broadcast.send_pyobj(configuration.ZMQ_STOP_POWER_COLLECTION)

    def ZMQ_shutdown(self):
        self.broadcast.close()
        self.context.term()
        del self.context
        del self.broadcast
