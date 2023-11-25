import os
import flwr as fl
import argparse
import csv
import math
import tensorflow as tf

parser = argparse.ArgumentParser(description="Flower Embedded devices")
NUM_CLIENTS = -1
PI_NAME = ""

with open("Outputs/Experiments/epoch_logs.csv", "w") as f:
    ...

def add_parser_args(p):
    p.add_argument(
        "--agg_ip",
        type=str,
        default="0.0.0.0",
        help=f"gRPC server address IP (default '0.0.0.0')",
    )
    p.add_argument(
        "--agg_port",
        type=str,
        default="8080",
        help=f"gRPC server address port (default '8080')",
    )
    p.add_argument(
        "--cid",
        type=int,
        required=True,
        help="Client id. Should be an integer between 0 and NUM_CLIENTS",
    )
    p.add_argument(
        "--dataset",
        type=str,
        required=True,
        help="Choose a dataset from the list of valid datasets",
    )
    p.add_argument(
        "--client_ip",
        type=str,
        default="0.0.0.0",
        help=f"Client IP Address (default '0.0.0.0')",
    )
    p.add_argument(
        "--num_parties",
        type=int,
        default=2,
        help=f"Number of Parties participating in FL (default 2)",
    )
    p.add_argument(
        "--pi_name",
        type=str,
        required=True,
        help=f"Name of the RPI",
    )


add_parser_args(parser)

args = parser.parse_args()
NUM_CLIENTS = args.num_parties
PI_NAME = args.pi_name

from common.Flower_Clients import DaSHFlowerClient

def prepare_dataset(use_mnist: bool):
    """Download and partitions the CIFAR-10/MNIST dataset."""
    global NUM_CLIENTS

    if use_mnist:
        (x_train, y_train), testset = tf.keras.datasets.mnist.load_data()
    else:
        (x_train, y_train), testset = tf.keras.datasets.cifar10.load_data()
    partitions = []
    # We keep all partitions equal-sized in this example
    partition_size = math.floor(len(x_train) / NUM_CLIENTS)
    for cid in range(NUM_CLIENTS):
        # Split dataset into non-overlapping NUM_CLIENT partitions
        idx_from, idx_to = int(cid) * partition_size, (int(cid) + 1) * partition_size

        x_train_cid, y_train_cid = (
            x_train[idx_from:idx_to] / 255.0,
            y_train[idx_from:idx_to],
        )

        # now partition into train/validation
        # Use 10% of the client's training data for validation
        split_idx = math.floor(len(x_train_cid) * 0.9)

        client_train = (x_train_cid[:split_idx], y_train_cid[:split_idx])
        client_val = (x_train_cid[split_idx:], y_train_cid[split_idx:])
        partitions.append((client_train, client_val))

    return partitions, testset

def main():
    use_mnist = True if args.dataset == "mnist" else False

    # Download CIFAR-10 dataset and partition it
    partitions, _ = prepare_dataset(use_mnist)
    trainset, valset = partitions[args.cid]

    server_address = args.agg_ip + ":" + args.agg_port

    # Start Flower client setting its associated data partition
    fl.client.start_numpy_client(
        server_address=server_address,
        client=DaSHFlowerClient(trainset=trainset, valset=valset, use_mnist=use_mnist),
    )

    # Epoch Logs made prettier
    with open('Outputs/Experiments/epoch_logs.csv','r') as f, open('Outputs/Experiments/temp.csv','w',newline='') as g:
        rdr = csv.reader(f)
        wtr = csv.writer(g)
        round_count = 1
        previous_epoch = 0

        for row in rdr:
            epoch, start, end = row
            epoch = int(epoch)
            if epoch > previous_epoch:
                previous_epoch = epoch
            else:
                round_count+=1
                previous_epoch = epoch
            wtr.writerow((
                round_count,
                epoch,
                start,
                end
            ))
    os.remove(r'Outputs/Experiments/epoch_logs.csv')
    os.rename(r'Outputs/Experiments/temp.csv', r'Outputs/Experiments/epoch_logs.csv')
    
main()