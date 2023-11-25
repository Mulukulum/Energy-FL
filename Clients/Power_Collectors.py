from Clients.Party import sshRunner, Party

class PowerCollector:
    
    def __init__(self, ip: str, username: str, collection_party : Party, bluetooth_address : str, zmq_broadcast_port : int ) -> None:
        self.ip = ip
        self.username = username
        self.ssh = sshRunner(f"{self.username}@{self.ip}")
        self.party = collection_party
        self.tester_address = bluetooth_address 
        self.broadcast_port = zmq_broadcast_port
        
    def pair_to_tester(self):
        self.ssh.run(["./Clients/Scripts/connect_to_bt_multimeter.sh ;"])
    
    def collect_power_data(self):
        self.ssh.run(["./Clients/Scripts/power_collector.py ;"])

