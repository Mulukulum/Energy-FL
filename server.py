import argparse
from typing import List, Tuple

import flwr as fl
from flwr.common import Metrics

import sys
import os
import subprocess
import time

import zmq

# Constants
BEGIN_EVAL = 100
BEGIN_EVAL_POST_SYNC = 101
PARTY_STARTED = 200
EVAL_FINISHED = 201
EVAL_FINISHED_POST_SYNC = 202
PARTY_CLOSING = 404
STOP_POWER_COLLECTION = 300

ips = {
    "user": "10.8.1.46",
    "rpi1": "10.8.1.38",
    "rpi3": "10.8.1.192",
}

ports_listening = {
    "rpi1": 6012,
    "rpi3": 6013,
}

broadcast_port = 6011
aggregator_username = "user"
aggregator_ip = ips.get("user")

# Data Generation
valid_datasets = {"mnist", "cifar10"}
valid_fusion_algos = {
    "FedAvg",
    "FedProx",
    "FedAdagrad",
    "FedXgbNnAvg",
}

fusion_algos_translator = {
    "FedAvg": fl.server.strategy.FedAvg,
    "FedProx": fl.server.strategy.FedProx,
    "FedAdagrad": fl.server.strategy.FedAdagrad,
    "FedXgbNnAvg": fl.server.strategy.FedXgbNnAvg,
}


valid_models = {"tf-cnn"}

# Parameters
rounds = 3
epochs = 4
run = "0"

dataset = "mnist"
num_parties: int = 2
batch_size = 512
fusion = "FedAvg"
model = "tf-cnn"
sample_fraction = 1.0

min_num_clients = num_parties
fusion = fusion_algos_translator[fusion]


# Define metric aggregation function
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


def main(args: dict = None):
    '''
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
    ```
    
    '''
    if args is not None:
        for key,val in args.items():
            exec(key + "=" + str(val) ) # This is bad but its quick

    print("\n" * 3)

    if num_parties != len(ips) - 1:
        print("""WARNING! Number of parties and number of provided IPs do not match.""")
        print("""Change the dictionary of IPs in this python script rfn""")
        input("Press Enter to Exit")
        sys.exit()

    if run is None:
        input(
            """
          Note : If you need SAR Timeseries data for multiple devices,
          specify that in the sar_timeseries_userlist at the end of the file
          Add each username as a string into the list
          Don't forget to change the following Scripts
          1.) sar_collector.sh [located in the Functions Directory]
          2.) The 'ips' dictionary of this python file. Leave only those IPs that are participating
          3.) The 'ports_listening' dictionary of this python file. Leave only the parties that are participating
          Edit the hosts and IPs list in these files if required and Press Enter to continue\n
          """
        )

    print(
        f"""
      {'' if run is None else f'{run=}'}
      {rounds=}
      {epochs=}
      {dataset=}
      {num_parties=}
      {batch_size=}
      {fusion=}
      {model=}
      """
    )

    # Define strategy
    strategy = fl.server.strategy.FedAvg(
        fraction_fit=sample_fraction,
        fraction_evaluate=sample_fraction,
        min_fit_clients=min_num_clients,
        on_fit_config_fn=fit_config,
        evaluate_metrics_aggregation_fn=weighted_average,
    )

    agg_context = zmq.Context()
    listeners = []
    try:
        for user, port in ports_listening.items():
            a = agg_context.socket(zmq.SUB)
            a.setsockopt(zmq.SUBSCRIBE, b"")
            a.connect(f"tcp://{ips.get(user)}:{port}")
            listeners.append(a)

        broadcast = agg_context.socket(zmq.PUB)
        broadcast.bind(f"tcp://{aggregator_ip}:{broadcast_port}")
    except OSError as e:
        print(f"OSError Occurred, Error {e}")

    
        

    # We listen for the the parties to confirm they actually did stuff
    def wait_until_ready(value, msg=None) -> None:
        nonlocal listeners
        if msg is None:
            msg = f"Listening for value : {value}"
        print(msg)
        finished = [False] * len(listeners)
        finished_indicies = []
        while False in finished:
            for index, listener in enumerate(listeners):
                if index in finished_indicies:
                    continue
                try:
                    response = listener.recv_pyobj(flags=zmq.NOBLOCK)
                except zmq.ZMQError:
                    ...
                else:
                    if response == value:
                        finished_indicies.append(index)
                        finished[index] = True
            print(f"Parties that have responded :", *finished_indicies, sep=" ")
            if False not in finished:
                time.sleep(5)
            else:
                time.sleep(15)
        print("Finished Waiting")

    # Start Flower server

    sar = subprocess.Popen(["./Functions/sar_collector.sh"], stdin=subprocess.PIPE)
    power = subprocess.Popen(["./Functions/power_collector.sh", "0.5"])
    party_id = 0
    for user, ip in ips.items():
        if user == aggregator_username:
            continue
        subp = subprocess.Popen(
            [
                "./Functions/pi_runner.sh",
                fusion,
                model,
                str(num_parties),
                dataset,
                aggregator_ip,
                ip,
                str(broadcast_port),
                str(ports_listening.get(user)),
                user,
                str(party_id),
                str(batch_size),
            ]
        )
        party_id += 1
        time.sleep(2)

    fl.server.start_server(
        server_address=args.server_address,
        config=fl.server.ServerConfig(num_rounds=3),
        strategy=strategy,
    )

    sar.communicate(b"\n")
    broadcast.send_pyobj(STOP_POWER_COLLECTION)
    sar.wait()
    power.wait()
    
    # FL Training is Done, now for the evaluations
    
    

    for listener in listeners:
        try:
            listener.close()
        except Exception:
            print("Close Failed")
    broadcast.close()
    agg_context.term()

    for user, ip in ips.items():
        if user != aggregator_username:
            subprocess.run(f"./Functions/files_copier.sh {user} {ip}", shell=True)

    if run is None:
        fname = f"{fusion}_{model}_{batch_size}_{num_parties}_{dataset}"
    else:
        fname = f"{fusion}_{model}_{batch_size}_{num_parties}_{dataset}_{run}"

    from Functions import Parser

    Parser.main(
        party_usernames=list(ips.keys()),
        name=fname,
        sar_timeseries_userlist=list(ips.keys()),
    )


if __name__ == "__main__":
    main()
    sys.exit()