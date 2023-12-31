from typing import List, Tuple
from flwr.common import Metrics
from common import configuration as config
from common import experiments
import flwr as fl

rounds = -1
epochs = -1
batch_size = -1


def weighted_average(metrics: List[Tuple[int, Metrics]]) -> Metrics:
    """Thist function averages the `accuracy` metric sent by the clients in a `evaluate`
    stage (i.e. clients received the global model and evaluate it on their local
    validation sets)."""
    # Multiply accuracy of each client by number of examples used
    accuracies = [num_examples * m["accuracy"] for num_examples, m in metrics]
    examples = [num_examples for num_examples, _ in metrics]

    # Aggregate and return custom metric (weighted average)
    return {"accuracy": sum(accuracies) / sum(examples)}


def fit_config(server_round: int):
    """Return a configuration with static batch size and (local) epochs."""
    global epochs, batch_size
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


def main(args: dict = None):
    """
    Pass args as a dictionary with the keys :

    ```
    rounds
    epochs
    run
    dataset
    batch_size
    fusion
    model
    sample_fraction
    proximal_mu
    ```
    """

    global rounds, epochs, run, dataset, batch_size, model
    min_num_clients = len(config.IP_CLIENTS)

    if args is not None:
        rounds = args["rounds"]
        epochs = args["epochs"]
        run = args["run"]
        dataset = args["dataset"]
        batch_size = args["batch_size"]
        fusion = args["fusion"]
        model = args["model"]
        sample_fraction = args["sample_fraction"]
        proximal_mu = args.get("proximal_mu", 1)

    fusion = experiments.FUSION_ALGOS_TRANSLATOR[fusion]
    # Define strategy

    if fusion == experiments.FUSION_ALGOS_TRANSLATOR["FedProx"]:
        strategy = fusion(
            fraction_fit=sample_fraction,
            fraction_evaluate=sample_fraction,
            min_fit_clients=min_num_clients,
            on_fit_config_fn=fit_config,
            min_available_clients=min_num_clients,
            evaluate_metrics_aggregation_fn=weighted_average,
            on_evaluate_config_fn=evaluate_config,
            proximal_mu=proximal_mu,
        )
    else:
        strategy = fusion(
            fraction_fit=sample_fraction,
            fraction_evaluate=sample_fraction,
            min_fit_clients=min_num_clients,
            on_fit_config_fn=fit_config,
            min_available_clients=min_num_clients,
            evaluate_metrics_aggregation_fn=weighted_average,
            on_evaluate_config_fn=evaluate_config,
        )

    server_address = (
        str(config.IP_AGGREGATOR) + ":" + str(config.AGGREGATOR_FLOWER_SERVER_PORT)
    )

    fl.server.start_server(
        server_address=server_address,
        config=fl.server.ServerConfig(num_rounds=rounds),
        strategy=strategy,
    )
