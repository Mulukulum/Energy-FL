from Clients.Party import sshRunner, Party
from common import Experiment
class PowerCollector:
    
    def __init__(self, ip: str, username: str, collection_party : Party, bluetooth_address : str, zmq_broadcast_port : int, experiment : Experiment ) -> None:
        self.ip = ip
        self.username = username
        self.ssh = sshRunner(f"{self.username}@{self.ip}")
        self.party = collection_party
        self.tester_address = bluetooth_address 
        self.broadcast_port = zmq_broadcast_port
        self.experiment_name = experiment.folder_name
        
    def pair_to_tester(self):
        self.ssh.run([f"./Clients/Scripts/connect_to_bt_multimeter.sh {self.tester_address} ;"])
    
    def collect_power_data(self):
        self.ssh.Popen([f"""./Clients/Scripts/power_collector.py --filename "{self.experiment_name}_{self.party.username}" --port {self.broadcast_port} --address {self.tester_address} ;"""])

