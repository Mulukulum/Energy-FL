import flwr as fl
import tensorflow as tf
from tensorflow import keras


class DaSHFlowerClient(fl.client.NumPyClient):
    """A FlowerClient that uses MobileNetV3 for CIFAR-10 or a much smaller CNN for
    MNIST. Ideally this client should never be used"""

    def __init__(self, trainset, valset, use_mnist: bool, name: str, expt_folder_name : str):
        import pathlib
        
        self.x_train, self.y_train = trainset
        self.x_val, self.y_val = valset
        self.name = name
        self.experiment_folder_name = expt_folder_name
        pathlib.Path(f"Outputs/Experiments/{self.experiment_folder_name}").mkdir(parents=True, exist_ok=True)
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
                "accuracy",
            ],
        )

    def get_parameters(self, config):
        return self.model.get_weights()

    def set_parameters(self, params):
        self.model.set_weights(params)

    def fit(self, parameters, config):
        from common.epoch_logger import TimeHistory
        fl.common.logger.logger.info("Client Sampled for fit()")
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

        start_times = epoch_time_logger.start_times
        end_times = epoch_time_logger.end_times

        import csv

        with open(f"Outputs/Experiments/{self.experiment_folder_name}/epoch_logs.csv", "a", newline="") as f:
            writer = csv.writer(f)
            for index, (start_time, end_time) in enumerate(zip(start_times, end_times)):
                format = (
                    index + 1,
                    start_time,
                    end_time,
                )
                writer.writerow(format)
        return self.get_parameters({}), len(self.x_train), {}

    def evaluate(self, parameters, config):
        self.set_parameters(parameters)
        (
            loss,
            accuracy,
        ) = self.model.evaluate(self.x_val, self.y_val)

        multilabel_average_options = ["micro", "macro", "weighted"]
        metrics_dictionary = {
            "acc": round(accuracy, 2),
            "accuracy": accuracy,
            "loss": loss,
        }
        if config.get("log_final", False):
            ...
        else:
            return loss, len(self.x_val), metrics_dictionary

        import numpy as np
        from sklearn.metrics import f1_score, precision_score, recall_score

        y_pred1 = self.model.predict(self.x_val)
        y_pred = np.argmax(y_pred1, axis=1)
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
            f'Outputs/Experiments/{self.experiment_folder_name}/{self.name}{config.get("synced", "")}.txt', "w"
        ) as f:
            f.write(str(metrics_dictionary))

        return loss, len(self.x_val), metrics_dictionary
