# Experiments Setup

# * This file contains everything a client needs to know about an FL experiment

import flwr as fl

# Let us initialize all the parameters that we will be using for testing

__version__ = "v0.1"

valid_fusions = [
    "FedAvg",
    "FedProx",
]

valid_models = [
    "tf-cnn",
]

valid_datasets = [
    "cifar10",
    "mnist",
]

# Initializing params that are not required for every experiment

valid_proximal_mu: list[float] = [1.0]

fusion_translator = {
    "FedAvg": fl.server.strategy.FedAvg,
    "FedProx": fl.server.strategy.FedProx,
}


class Experiment:
    # * this entire class should probably be a dataclass but I decided to write it manually since i'm not familiar with dataclasses

    def __init__(
        self,
        model: str,
        fusion: str,
        dataset: str,
        batch_size: int,
        rounds: int,
        epochs: int,
        proximal_mu: float = 0,
        sample_fraction: float = 1.0,
        version: str = __version__,
        num_parties: int = None,
        run: int = None,
    ) -> None:
        self.model = model
        self.fusion = fusion
        self.dataset = dataset
        self.batch_size = batch_size
        self.rounds = rounds
        self.epochs = epochs
        self.sample_fraction = sample_fraction
        self.proximal_mu = proximal_mu
        self.version = version
        self.num_participating_parties = num_parties
        self.check_validity()
        self.run = run
        self.folder_name = f"{self.version};{self.model};{self.fusion};{self.dataset};{self.batch_size};{self.rounds};{self.epochs};{self.sample_fraction};{self.proximal_mu};{self.num_participating_parties};{self.run}"

    def __eq__(self, __value) -> bool:
        if self.__class__ is not __value.__class__:
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
            self.num_participating_parties,
            self.run,
        ) != (
            __value.model,
            __value.fusion,
            __value.dataset,
            __value.batch_size,
            __value.rounds,
            __value.epochs,
            __value.sample_fraction,
            __value.proximal_mu,
            __value.version,
            __value.num_participating_parties,
            __value.run,
        ):
            return False

        return True

    def __ne__(self, __value: object) -> bool:
        return not (self == __value)

    def __hash__(self) -> int:
        return hash(
            (
                (
                    self.__class__,
                    self.model,
                    self.fusion,
                    self.dataset,
                    self.batch_size,
                    self.rounds,
                    self.epochs,
                    self.sample_fraction,
                    self.proximal_mu,
                    self.version,
                    self.num_participating_parties,
                    self.run,
                )
            )
        )

    def __repr__(self) -> str:
        return f"""
    Version : {self.version}
    Model : {self.model}
    Fusion : {self.fusion}
    Dataset : {self.dataset}
    Batch-Size : {self.batch_size}
    Rounds : {self.rounds}
    Epochs : {self.epochs}
    Sample-Fraction : {self.sample_fraction}
    Proximal-Mu : {self.proximal_mu}
    Number of Parties : {self.num_participating_parties}
    Run Number : {self.run}
        """

    def check_validity(self):
        if self.model not in valid_models:
            raise ValueError(f"{self.model} is not a valid model")
        if self.fusion not in valid_fusions:
            raise ValueError(f"{self.fusion} is not a valid fusion")
        if self.dataset not in valid_datasets:
            raise ValueError(f"{self.dataset} is not a valid dataset")
        if not (0.0 <= self.sample_fraction <= 1.0):
            raise ValueError(f"{self.sample_fraction} is not a valid sample-fraction")
        if not (0 <= self.proximal_mu):
            raise ValueError(f"{self.proximal_mu} is not a valid proximal-mu")


def generate_all_experiments(
    rounds_and_epochs: list[tuple[int, int]],
    batch_sizes: list[int],
    runs: int,
    num_parties: int,
) -> list[Experiment]:
    all_experiments = []
    for dataset in valid_datasets:
        for model in valid_models:
            for fusion in valid_fusions:
                for rounds, epochs in rounds_and_epochs:
                    for batch_size in batch_sizes:
                        for run in range(1, runs + 1):
                            expt = Experiment(
                                model=model,
                                fusion=fusion,
                                dataset=dataset,
                                batch_size=batch_size,
                                rounds=rounds,
                                epochs=epochs,
                                num_parties=num_parties,
                                run=run,
                            )

                            all_experiments.append(expt)

    return all_experiments
