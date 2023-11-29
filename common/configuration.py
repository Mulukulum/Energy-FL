# ! This file contains the device configurations for the experiments

# * Stuff like the IPs of the devices, ZMQ Ports and Which device is collecting power for which other device etc is here

import logging
import getpass

VALID_FUSION_ALGOS = [
    "FedAvg",
    "FedProx",
]

VALID_MODELS = [
    "tf-cnn",
]

VALID_DATASETS = [
    "mnist",
    "cifar10"
]

VALID_PROXIMAL_MU: list[float] = [1.0]

IP_CLIENTS = {
    "rpi1": "10.8.1.38",
    "rpi2": "10.8.1.43",
    "rpi3": "10.8.1.192",
    "rpi4": "10.8.1.41",
}

IP_AGGREGATOR = "10.8.1.45"

AGGREGATOR_FLOWER_SERVER_PORT = 7011

DEVICE_USERNAME = getpass.getuser()

AGGREGATOR_ZMQ_BROADCAST_PORT = 6010

ZMQ_STOP_POWER_COLLECTION = 300

IP_POWER_COLLECTORS = {
    "pi2": "10.8.1.35",
}

UM25C_ADDR_FOR_POWER_COLLECTORS = {
    "pi2": "98:DA:F0:00:4A:13",
}

POWER_COLLECTOR_CONNECTED_DEVICE = {
    "pi2": "rpi1",
}

LOGGING_LEVEL = logging.DEBUG