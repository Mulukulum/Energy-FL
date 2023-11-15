import math
import argparse
import warnings
import datetime
import csv

from sklearn.metrics import f1_score, precision_score, recall_score
import flwr as fl
import tensorflow as tf
from tensorflow.keras.callbacks import Callback
from tensorflow import keras

#! Used for typehints only, remove when done
from keras.callbacks import Callback
import keras

#! Used for typehints only, remove when done


parser = argparse.ArgumentParser(description="Flower Embedded devices")
NUM_CLIENTS = -1
PI_NAME = ""

with open("Outputs/epoch_logs.csv", "w") as f:
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

class TimeHistory(Callback):
    def on_train_begin(self, logs={}):
        self.start_times = []
        self.end_times = []
        # self.times = []

    def on_epoch_begin(self, batch, logs={}):
        self.epoch_time_start = datetime.datetime.now()
        self.start_times.append(self.epoch_time_start)

    def on_epoch_end(self, batch, logs={}):
        self.epoch_time_end = datetime.datetime.now()
        self.end_times.append(self.epoch_time_end)
        # self.times.append(self.epoch_time_end - self.epoch_time_start)

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
        epoch_time_logger = TimeHistory()
        self.model.fit(
            self.x_train,
            self.y_train,
            epochs=epochs,
            batch_size=batch,
            callbacks=[epoch_time_logger],
        )

        # Logs Epoch Times
        start_times = epoch_time_logger.start_times
        end_times = epoch_time_logger.end_times
        with open("Outputs/epoch-logs.csv", "a", newline="") as f:
            writer = csv.writer(f)
            for index, (start_time, end_time) in enumerate(zip(start_times, end_times)):
                format = (
                    index + 1,
                    start_time.strftime(r"%H:%M:%S"),
                    end_time.strftime(r"%H:%M:%S"),
                )
                writer.writerow(format)
        return self.get_parameters({}), len(self.x_train), {}

    def evaluate(self, parameters, config):
        global PI_NAME
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
        if config.get("log_final", False):
            ...
        else:
            return loss, len(self.x_val), metrics_dictionary

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

        with open(
            f'Outputs/Evaluations/{PI_NAME}{config.get("synced", "")}.txt', "w"
        ) as f:
            f.write(str(metrics_dictionary))

        return loss, len(self.x_val), metrics_dictionary


def main():
    use_mnist = True if args.dataset == "mnist" else False

    # Download CIFAR-10 dataset and partition it
    partitions, _ = prepare_dataset(use_mnist)
    trainset, valset = partitions[args.cid]

    server_address = args.agg_ip + ":" + args.agg_port

    # Start Flower client setting its associated data partition
    fl.client.start_numpy_client(
        server_address=server_address,
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


with open('Outputs/epoch_logs.csv','r') as f, open('Outputs/temp.csv','w',newline='') as g:
    rdr = csv.reader(f)
    wtr = csv.writer(g)
    round_count = 1
    previous_epoch = 0
    
    for row in rdr:
        epoch, timestamp = row
        epoch = int(epoch)
        if epoch > previous_epoch:
            previous_epoch = epoch
        else:
            round_count+=1
            previous_epoch = epoch
        wtr.writerow((
            round_count,
            epoch,
            timestamp,
        ))

os.remove(r'Outputs/epoch_logs.csv')
os.rename(r'Outputs/temp.csv', r'Outputs/epoch_logs.csv')

"""
