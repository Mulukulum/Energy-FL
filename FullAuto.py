from server import main
import time

valid_datasets = ["mnist", "cifar10"]
valid_fusion_algos = [
    "FedAvg",
    "FedProx",
    "FedXgbNnAvg",
]
valid_models = ["tf-cnn"]
rounds_and_epochs = [
    (3, 4),
]
batch_sizes = [16, 512]
sample_fractions = (1.0,)
runs = 4

for dataset in valid_datasets:
    for model in valid_models:
        for fusion in valid_fusion_algos:
            for rounds_epochs in rounds_and_epochs:
                rounds, epochs = rounds_epochs
                for batch_size in batch_sizes:
                    for sample_fraction in sample_fractions:
                        for run in range(1, runs+1):
                            main(
                                {
                                    "rounds": rounds,
                                    "epochs": epochs,
                                    "run": run,
                                    "dataset": dataset,
                                    "batch_size": batch_size,
                                    "fusion": fusion,
                                    "model": model,
                                    "sample_fraction": sample_fraction,
                                }
                            )
