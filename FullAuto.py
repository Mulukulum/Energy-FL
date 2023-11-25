#! File to run experiments

run_finished_experiments = False

from common.Experiments import generate_all_experiments
from common import Experiment
from Clients import Aggregator, Party, PowerCollector
import common.Configuration as Configuration

experiments = generate_all_experiments()


def run_experiment(expt : Experiment):
    
    print(expt)
    
    #Setup all the clients, aggregators and power collectors
    
    
    

