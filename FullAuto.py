#! File to run experiments

run_finished_experiments = False

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

    #Setup all the clients, aggregators and power collectors
    
    agg = Aggregator(ip=Configuration.IP_AGGREGATOR, username='user', flwrPort=Configuration.AGGREGATOR_FLOWER_SERVER_PORT, zmqPort=Configuration.AGGREGATOR_ZMQ_BROADCAST_PORT)
    agg.setupZMQ()
    
    

