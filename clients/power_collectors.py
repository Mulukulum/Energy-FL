from clients.party import sshRunner, Party
from common.experiments import Experiment
import subprocess

class PowerCollector:
    def __init__(
        self,
        ip: str,
        username: str,
        collection_party_username: str,
        bluetooth_address: str,
        zmq_broadcast_port: int,
        experiment: Experiment,
        paired : bool = False,
    ) -> None:
        self.ip = ip
        self.username = username
        self.ssh = sshRunner(f"{self.username}@{self.ip}")
        self.party_username = collection_party_username
        self.tester_address = bluetooth_address
        self.broadcast_port = zmq_broadcast_port
        self.experiment_folder_name = experiment.folder_name
        self.experiment_name = f"{self.experiment_folder_name}_{self.party_username}"
        self.paired = paired

    def __repr__(self) -> str:
        return f"{self.party_username}@{self.ip} using {self.tester_address} to log {self.party_username}"

    def pair_to_tester(self):
        return self.ssh.Popen(
            [f"./clients/scripts/connect_to_bt_multimeter.sh {self.tester_address} ;"]
        )

    def collect_power_data(self, agg_ip: str):
        self.ssh.Popen(
            [
                f"""python -m clients.scripts.power_collector --filename "{self.experiment_name}" --zmq_ip {agg_ip}:{self.broadcast_port} --address {self.tester_address} ;"""
            ]
        )
    
    def copy_files_to_aggregator(self) -> bool:
        subprocess.run([f"scp {self.ssh.client}:~/Energy-FL/Outputs/Power/{self.experiment_name}.pkl ~/Energy-FL/Outputs/Experiments/{self.experiment_folder_name}/"], shell=True)
        from pickle import load
        with open(f"Outputs/Experiments/{self.experiment_folder_name}/{self.experiment_name}.pkl","rb") as f:
            val : dict = load(f)
            return val.get("success", False)
    
    def reboot_collector(self):
        self.ssh.run(['echo "user123" | sudo -S reboot ;'])
