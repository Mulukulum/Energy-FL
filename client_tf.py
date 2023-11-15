import math
import argparse
import warnings

from sklearn.metrics import f1_score, precision_score, recall_score
import flwr as fl
import tensorflow as tf
from tensorflow import keras as keras

parser = argparse.ArgumentParser(description="Flower Embedded devices")


def add_parser_args(p):
    p.add_argument(
        "--agg_ip",
        type=str,
        default="0.0.0.0:8080",
        help=f"gRPC server address (default '0.0.0.0:8080')",
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
        help="Choose a dataset from the list of valid datasets",
    )
    p.add_argument(
        "--client_ip",
        type=str,
        default="0.0.0.0:8080",
        help=f"Client IP Address (default '0.0.0.0:8080')",
    )
    p.add_argument(
        "--num_parties",
        type=int,
        default=2,
        help=f"Number of Parties participating in FL (default 2)",
    )
    p.add_argument(
        "--agg_broadcast_port",
        type=int,
        default=6011,
        help=f"Aggregator ZMQ Broadcast port",
    )
    p.add_argument(
        "--party_listener_port",
        type=int,
        default=-1,
        help=f"Listening port of party",
    )
    p.add_argument(
        "--pi_name",
        type=str,
        required=True,
        help = 'Username of the RPI'
    )


add_parser_args(parser)

warnings.filterwarnings("ignore", category=UserWarning)


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


class FlowerClient(fl.client.NumPyClient):
    """A FlowerClient that uses MobileNetV3 for CIFAR-10 or a much smaller CNN for
    MNIST."""

    def __init__(self, trainset, valset, use_mnist: bool):
        self.x_train, self.y_train = trainset
        self.x_val, self.y_val = valset
        # Instantiate model
        if use_mnist:
            # small model for MNIST
            self.model = keras.Sequential(
                [
                    keras.Input(shape=(28, 28, 1)),
                    keras.layers.Conv2D(32, kernel_size=(5, 5), activation="relu"),
                    keras.layers.MaxPooling2D(pool_size=(2, 2)),
                    keras.layers.Conv2D(64, kernel_size=(3, 3), activation="relu"),
                    keras.layers.MaxPooling2D(pool_size=(2, 2)),
                    keras.layers.Flatten(),
                    keras.layers.Dropout(0.5),
                    keras.layers.Dense(10, activation="softmax"),
                ]
            )
        else:
            # let's use a larger model for cifar
            self.model = tf.keras.applications.MobileNetV3Small(
                (32, 32, 3), classes=10, weights=None
            )
        self.model.compile(
            "adam",
            "sparse_categorical_crossentropy",
            metrics=[
                tf.keras.metrics.Accuracy(),
                tf.keras.metrics.F1Score(),
                tf.keras.metrics.Precision(),
            ],
        )

    def get_parameters(self, config):
        return self.model.get_weights()

    def set_parameters(self, params):
        self.model.set_weights(params)

    def fit(self, parameters, config):
        print("Client sampled for fit()")
        self.set_parameters(parameters)
        # Set hyperparameters from config sent by server/strategy
        batch, epochs = config["batch_size"], config["epochs"]
        # train
        self.model.fit(self.x_train, self.y_train, epochs=epochs, batch_size=batch)
        return self.get_parameters({}), len(self.x_train), {}

    def evaluate(self, parameters, config):
        self.set_parameters(parameters)
        (
            loss,
            accuracy,
            f1,
            precision,
        ) = self.model.evaluate(self.x_val, self.y_val)

        multilabel_average_options = ["micro", "macro", "weighted"]
        metrics_dictionary = {
            "acc": round(accuracy, 2),
            "accuracy": accuracy,
            "f1": f1,
            "precision": precision,
        }

        y_pred = self.model.predict(self.x_val)
        for avg in multilabel_average_options:
            metrics_dictionary["f1 " + avg] = round(
                f1_score(self.y_val, y_pred, average=avg, zero_division=0), 3
            )
            metrics_dictionary["precision " + avg] = round(
                precision_score(self.y_val, y_pred, average=avg, zero_division=0), 3
            )
            metrics_dictionary["recall " + avg] = round(
                recall_score(self.y_val, y_pred, average=avg, zero_division=0), 3
            )

        return loss, len(self.x_val), metrics_dictionary


def main():
    args = parser.parse_args()

    NUM_CLIENTS = args.num_parties
    
    assert args.cid < NUM_CLIENTS
    
    use_mnist = args.mnist
    # Download CIFAR-10 dataset and partition it
    partitions, _ = prepare_dataset(use_mnist)
    trainset, valset = partitions[args.cid]

    # Start Flower client setting its associated data partition
    fl.client.start_numpy_client(
        server_address=args.server_address,
        client=FlowerClient(trainset=trainset, valset=valset, use_mnist=use_mnist),
    )

    # Evaluate the results and store them into disk now


if __name__ == "__main__":
    main()

"""

from sklearn.metrics import f1_score, precision_score, recall_score, confusion_matrix
y_pred1 = model.predict(X_test)
y_pred = np.argmax(y_pred1, axis=1)

# Print f1, precision, and recall scores
print(precision_score(y_test, y_pred , average="macro"))
print(recall_score(y_test, y_pred , average="macro"))
print(f1_score(y_test, y_pred , average="macro"))


metrics = {}
    round_digits = 2
    multilabel_average_options = ["micro", "macro", "weighted"]

    for avg in multilabel_average_options:
        try:
            metrics["f1 " + avg] = round(f1_score(y_true, y_pred, average=avg, zero_division=0), round_digits)
            metrics["precision " + avg] = round(
                precision_score(y_true, y_pred, average=avg, zero_division=0), round_digits
            )
            metrics["recall " + avg] = round(recall_score(y_true, y_pred, average=avg, zero_division=0), round_digits)
        except Exception as ex:
            logger.exception(ex)

    return metrics
"""
