from clients.party import sshRunner, Party
from common import Experiment

class PowerCollector:
    
    def __init__(self, ip: str, username: str, collection_party : Party, bluetooth_address : str, zmq_broadcast_port : int, experiment : Experiment ) -> None:
        self.ip = ip
        self.username = username
        self.ssh = sshRunner(f"{self.username}@{self.ip}")
        self.party = collection_party
        self.tester_address = bluetooth_address 
        self.broadcast_port = zmq_broadcast_port
        self.experiment_name = f"{experiment.folder_name}_{self.party.username}"
        
    def pair_to_tester(self):
        return self.ssh.run([f"./clients/scripts/connect_to_bt_multimeter.sh {self.tester_address} ;"])
    
    def collect_power_data(self, agg_ip : str):
        self.ssh.Popen([f"""python clients/scripts/power_collector.py --filename "{self.experiment_name}" --zmq_ip {agg_ip}:{self.broadcast_port} --address {self.tester_address} ;"""])

