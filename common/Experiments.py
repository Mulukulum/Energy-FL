# Experiments Setup

# * This file contains everything a client needs to know about an FL experiment

import flwr as fl

# Let us initialize all the parameters that we will be using for testing

valid_fusions = ['FedAvg']
valid_models = ['tf-cnn']
valid_datasets = ['cifar10', 'mnist']

# Initializing params that are not required for every experiment

valid_proximal_mu: list[float] = [1.0]


class Experiment:
    fusion_translator = {
        "FedAvg": fl.server.strategy.FedAvg,
        "FedProx": fl.server.strategy.FedProx,
    }

    def __init__(
        self,
        model: str,
        fusion: str,
        dataset: str,
        batch_size: int,
        rounds: int,
        epochs: int,
        proximal_mu: float | None,
        sample_fraction: float = 1.0,
    ) -> None:
        self.model = model
        self.fusion = fusion
        self.dataset = dataset
        self.batch_size = batch_size
        self.rounds = rounds
        self.epochs = epochs
        self.sample_fraction = sample_fraction
        self.proximal_mu = proximal_mu
        self.check_validity()

    def check_validity(self):
        if self.model not in valid_models:
            raise ValueError(f"{self.model} is not a valid model")
        if self.fusion not in valid_fusions:
            raise ValueError(f"{self.fusion} is not a valid fusion")
        if self.dataset not in valid_models:
            raise ValueError(f"{self.dataset} is not a valid dataset")
        if not (0.0 < self.sample_fraction <= 1.0):
            raise ValueError(f"{self.sample_fraction} is not a valid sample-fraction")
        if not (0 <= self.proximal_mu):
            raise ValueError(f"{self.proximal_mu} is not a valid proximal-mu")
