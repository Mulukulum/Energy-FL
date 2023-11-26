#! File to run experiments

run_finished_experiments = False  # Change to True to re-run everything

import subprocess
from common import generate_all_experiments
from common import Experiment
from clients import Aggregator, Party, PowerCollector
from common import configuration
import time

batch_sizes = [16, 512]
rounds_and_epochs = [(3, 4)]
runs = 3
num_parties = len(configuration.IP_CLIENTS)

all_experiments = generate_all_experiments(
    rounds_and_epochs=rounds_and_epochs,
    batch_sizes=batch_sizes,
    runs=runs,
    num_parties=num_parties,
)


def run_experiment(expt: Experiment):
    print(expt)
    time.sleep(3)

    # Setup all the clients, aggregators and power collectors

    aggregator: Aggregator = Aggregator(
        ip=configuration.IP_AGGREGATOR,
        username=configuration.AGGREGATOR_USERNAME,
        flwrPort=configuration.AGGREGATOR_FLOWER_SERVER_PORT,
        zmqPort=configuration.AGGREGATOR_ZMQ_BROADCAST_PORT,
    )
    parties: list[Party] = [
        Party(ip=ip, username=username)
        for username, ip in configuration.IP_CLIENTS.items()
    ]

    bluetooth_collectors: list[PowerCollector] = []

    for user, ip in configuration.IP_POWER_COLLECTORS.items():
        party = configuration.POWER_COLLECTOR_CONNECTED_DEVICE[user]
        bt_addr = configuration.UM25C_ADDR_FOR_POWER_COLLECTORS[user]
        bluetooth_collectors.append(
            PowerCollector(
                ip=ip,
                username=user,
                collection_party=party,
                bluetooth_address=bt_addr,
                experiment=expt,
            )
        )

    from clients.scripts.old_server import main as run_flwr_server

    # Setup SAR
    from common import sar

    all_ips = configuration.IP_CLIENTS.copy()
    all_ips.update({configuration.AGGREGATOR_USERNAME: configuration.IP_AGGREGATOR})
    sar.initialize_sar(usernames_ips=all_ips)
    subprocess.run(["chmod u+x clients/scripts/sar_collector.sh"], shell=True)

    # Setup Bluetooth
    for collector in bluetooth_collectors:
        collector.pair_to_tester()

    # Ready to start the experiment

    # Start the Power Collections, SAR and then finally start the parties and the server

    for collector in bluetooth_collectors:
        collector.collect_power_data()

    sar_process = subprocess.Popen(
        ["./clients/scripts/sar_collector.sh"], shell=True, stdin=subprocess.PIPE
    )

    for cid, party in enumerate(parties):
        party.start_client_server(
            agg_ip=configuration.IP_AGGREGATOR,
            agg_port=configuration.AGGREGATOR_FLOWER_SERVER_PORT,
            cid=cid,
            dataset=expt.dataset,
            num_parties=expt.num_participating_parties,
        )

    args = {
        "rounds": expt.rounds,
        "epochs": expt.epochs,
        "run": expt.run,
        "dataset": expt.dataset,
        "batch_size": expt.batch_size,
        "fusion": expt.fusion,
        "model": expt.model,
        "sample_fraction": expt.sample_fraction,
        "proximal_mu": expt.proximal_mu,
    }

    run_flwr_server(args=args)

    sar_process.communicate(b"\n")
    aggregator.ZMQ_stop_power_collection()

    #! Done!


completed_experiments = Aggregator.get_completed_experiments()

for experiment in all_experiments:
    if experiment not in completed_experiments:
        run_experiment(experiment)
    elif run_finished_experiments:
        run_experiment(experiment)
