# Experiments Setup

# * This file contains everything a client needs to know about an FL experiment

import flwr as fl

# Let us initialize all the parameters that we will be using for testing

valid_fusions = []
valid_models = []
valid_datasets = []
valid_batch_sizes : list[int] = [16, 512]

valid_rounds : list[int] = [3]
valid_epochs : list[int] = [4]
valid_rounds_and_epochs = [
    # Rounds, Epochs
    (3,4)
]

valid_sample_fractions : list[float] = [1.0]

# Initializing params that don't run on every experiment


valid_proximal_mu : list[float] = [1.0]


