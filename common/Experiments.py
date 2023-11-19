# Experiments Setup

# * This file contains everything a client needs to know about an FL experiment

import flwr as fl

# Let us initialize all the parameters that we will be using for testing

__version__ = "v0.1"

valid_fusions = ["FedAvg", "FedProx"]
valid_models = [
    "tf-cnn",
]
valid_datasets = ["cifar10", "mnist"]

# Initializing params that are not required for every experiment

valid_proximal_mu: list[float] = [1.0]

class Experiment:
    # * this entire class should probably be a dataclass but I decided to write it manually since i'm not familiar with dataclasses

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
        proximal_mu: float = None,
        sample_fraction: float = 1.0,
        version: str = None,
        num_parties : int | None = None
    ) -> None:
        self.model = model
        self.fusion = fusion
        self.dataset = dataset
        self.batch_size = batch_size
        self.rounds = rounds
        self.epochs = epochs
        self.sample_fraction = sample_fraction
        self.proximal_mu = 0 if proximal_mu is None else proximal_mu
        self.version = __version__ if version is None else version
        self.num_participating_parties = num_parties
        self.check_validity()

    def __eq__(self, __value) -> bool:
        if self.__class__ is not __value.__class__ :
            return False
        if (
            self.model,
            self.fusion,
            self.dataset,
            self.batch_size,
            self.rounds,
            self.epochs,
            self.sample_fraction,
            self.proximal_mu,
            self.version,
            self.num_participating_parties
        ) != (__value.model,
         __value.fusion,
         __value.dataset,
         __value.batch_size,
         __value.rounds,
         __value.epochs,
         __value.sample_fraction,
         __value.proximal_mu,
         __value.version,
         __value.num_participating_parties): return False
        
        return True
    
    def __ne__(self, __value: object) -> bool:
        return not (self == __value )

    def check_validity(self):
        if self.model not in valid_models:
            raise ValueError(f"{self.model} is not a valid model")
        if self.fusion not in valid_fusions:
            raise ValueError(f"{self.fusion} is not a valid fusion")
        if self.dataset not in valid_models:
            raise ValueError(f"{self.dataset} is not a valid dataset")
        if not (0.0 <= self.sample_fraction <= 1.0):
            raise ValueError(f"{self.sample_fraction} is not a valid sample-fraction")
        if not (0 <= self.proximal_mu):
            raise ValueError(f"{self.proximal_mu} is not a valid proximal-mu")
