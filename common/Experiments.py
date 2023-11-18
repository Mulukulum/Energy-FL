# Experiments Setup

# * This file contains everything a client needs to know about an FL experiment

import flwr as fl

# Let us initialize all the parameters that we will be using for testing

valid_fusions = []
valid_models = []
valid_datasets = []
valid_batch_sizes : list[int] = [16, 512]
valid_sample_fractions : list[float] = [1.0]

valid_rounds : list[int] = [3]
valid_epochs : list[int] = [4]
valid_rounds_and_epochs = [
    # Rounds, Epochs
    (3,4)
]

# Initializing params that are not required for every experiment

valid_proximal_mu : list[float] = [1.0]

class Experiment():

    fusion_translator = {
        'FedAvg' : fl.server.strategy.FedAvg,
        'FedProx' : fl.server.strategy.FedProx,
    }
    
    def __init__(self, model : str, fusion : str, dataset : str, batch_size: int, sample_fraction : float, proximal_mu : float, rounds : int, epochs : int) -> None:
        self.model = model
        self.fusion = fusion
        self.dataset = dataset
        self.batch_size = batch_size
        self.sample_fraction = sample_fraction
        self.proximal_mu = proximal_mu
        self.rounds = rounds
        self.epochs = epochs
        


