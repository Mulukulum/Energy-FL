from typing import List, Tuple
from flwr.common import Metrics

from common.Configuration import IP_CLIENTS

rounds = 3
epochs = 4

dataset = "mnist"
num_parties: int = len(IP_CLIENTS) - 1 
batch_size = 32
fusion = "FedAvg"
model = "tf-cnn"
sample_fraction = 1.0
run = None
proximal_mu = 1


def weighted_average(metrics: List[Tuple[int, Metrics]]) -> Metrics:
    """Thist function averages the `accuracy` metric sent by the clients in a `evaluate`
    stage (i.e. clients received the global model and evaluate it on their local
    validation sets)."""
    # Multiply accuracy of each client by number of examples used
    accuracies = [num_examples * m["accuracy"] for num_examples, m in metrics]
    examples = [num_examples for num_examples, _ in metrics]

    # Aggregate and return custom metric (weighted average)
    return {"accuracy": sum(accuracies) / sum(examples)}


def fit_config(
    server_round: int, *_, epochs: int = epochs, batch_size: int = batch_size
):
    """Return a configuration with static batch size and (local) epochs."""
    config = {
        "epochs": epochs if epochs else 4,  # Number of local epochs done by clients
        "batch_size": batch_size
        if batch_size
        else 16,  # Batch size to use by clients during fit()
    }
    return config


def evaluate_config(server_round: int):
    global rounds
    if server_round == -1:
        log_final = True
        synced = "-synced"
    elif rounds == server_round:
        log_final = True
        synced = ""
    else:
        log_final = False
        synced = ""
    return {"log_final": log_final, "synced": synced}