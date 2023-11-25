#! File to run experiments

run_finished_experiments = False # Change to True to re-run everything

import subprocess
from common.Experiments import generate_all_experiments
from common import Experiment
from Clients import Aggregator, Party, PowerCollector
import common.Configuration as Configuration
import time

batch_sizes = [16, 512]
rounds_and_epochs = [
    (3,4)
]
runs = 3
num_parties = len(Configuration.IP_CLIENTS)

experiments = generate_all_experiments(rounds_and_epochs=rounds_and_epochs, batch_sizes=batch_sizes, runs=runs, num_parties=num_parties)

def run_experiment(expt : Experiment):
    
    
    print(expt)
    time.sleep(3)

    # Setup all the clients, aggregators and power collectors
    
    aggregator = Aggregator(ip=Configuration.IP_AGGREGATOR, username=Configuration.getuser, flwrPort=Configuration.AGGREGATOR_FLOWER_SERVER_PORT, zmqPort=Configuration.AGGREGATOR_ZMQ_BROADCAST_PORT)
    parties = [Party(ip=ip, username=username) for username, ip in Configuration.IP_CLIENTS.items()]
    
    bluetooth_collectors = [PowerCollector()]
    from Clients.Scripts.old_server import main as run_flwr_server
    
    # Setup SAR
    from common import sar
    all_ips = Configuration.IP_CLIENTS.copy()
    all_ips.update({Configuration.AGGREGATOR_USERNAME : Configuration.IP_AGGREGATOR})
    sar.initialize_sar(usernames_ips=all_ips)
    subprocess.run("chmod u+x Clients/Scripts/sar_collector.sh", shell=True)
    
    # Setup Bluetooth
    
    
    
    

