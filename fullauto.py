#! File to run experiments

run_finished_experiments = False  # Change to True to re-run everything

import gc
import time
import subprocess
from common.experiments import generate_all_experiments
from common.experiments import Experiment
from common.experiments import __version__
from clients.aggregator import Aggregator
from clients.party import Party
from clients.power_collectors import PowerCollector
from common import configuration
from common.database import get_completed_experiments
from common.log import energy_fl_logger

batch_sizes = [16, 64, 128, 256, 512]
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
    
    global paired
    
    expt.add_to_log()
    expt.set_running()
    time.sleep(3)
    
    SUCCESS = True
    ABORT = False
    
    energy_fl_logger.info("\n" + str(expt))
    time.sleep(3)

    # Setup all the clients, aggregators and power collectors
    
    expt.prepare_for_run(wipe_contents_if_exists=True)

    aggregator: Aggregator = Aggregator(
        ip=configuration.IP_AGGREGATOR,
        username=configuration.DEVICE_USERNAME,
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
                collection_party_username=party,
                bluetooth_address=bt_addr,
                zmq_broadcast_port=configuration.AGGREGATOR_ZMQ_BROADCAST_PORT,
                experiment=expt,
            )
        )

    from clients.scripts.old_server import main as run_flwr_server

    # Setup SAR
    from common import sar

    all_ips = configuration.IP_CLIENTS.copy()
    all_ips.update({configuration.DEVICE_USERNAME: configuration.IP_AGGREGATOR})

    sar.initialize_sar(usernames_ips=all_ips)
    subprocess.run(["chmod u+x clients/scripts/sar_collector.sh"], shell=True)

    for party in parties:
        if not party.check_client_online():
            ABORT = True
            SUCCESS = False
            energy_fl_logger.critical(f"Client {str(party)} was detected offline")
            expt.set_failed()
            expt.set_not_running()
            energy_fl_logger.error("Experiment Run Failed")
            SUCCESS = False
            ABORT = True
            energy_fl_logger.info("Sleeping for 3 minutes until next run")
            time.sleep(180)
            return

    # Setup Bluetooth
    for collector in bluetooth_collectors:
        if not paired:
            collector.pair_to_tester().wait()
        energy_fl_logger.info(f"{str(collector)} was paired to tester")
    paired = True
    # Ready to start the experiment

    aggregator.ZMQ_setup()
    # Start the Power Collections, SAR and then finally start the parties and the server

    for collector in bluetooth_collectors:
        collector.collect_power_data(agg_ip=configuration.IP_AGGREGATOR)

    energy_fl_logger.info("Power Collection Started")

    sar_process = subprocess.Popen(
        [f"./clients/scripts/sar_collector.sh {expt.folder_name}"], shell=True, stdin=subprocess.PIPE
    )

    energy_fl_logger.info("SAR Started. Waiting 5 seconds to start parties")
    time.sleep(5)

    for cid, party in enumerate(parties):
        party.start_client_server(
            agg_ip=configuration.IP_AGGREGATOR,
            agg_port=configuration.AGGREGATOR_FLOWER_SERVER_PORT,
            cid=cid,
            dataset=expt.dataset,
            num_parties=expt.num_participating_parties,
            expt_name=expt.folder_name
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
    
    for party in parties:
        if not party.check_client_online():
            ABORT = True
            SUCCESS = False
            energy_fl_logger.critical(f"Client {str(party)} was detected offline")
            expt.set_failed()
            expt.set_not_running()
            energy_fl_logger.error("Experiment Run Failed")
            SUCCESS = False
            ABORT = True
            energy_fl_logger.info("Sleeping for 3 minutes until next run")
            time.sleep(180)
            return

    try:
        run_flwr_server(args=args)
    except ValueError:
        energy_fl_logger.critical("Server received Failure from client. Aborting File Collection")
        expt.set_failed()
        expt.set_not_running()
        energy_fl_logger.error("Experiment Run Failed")
        SUCCESS = False
        ABORT = True
    energy_fl_logger.info("Flower Server Finished Running!")
    time.sleep(1)
    sar_process.communicate(b"\n")
    aggregator.ZMQ_stop_power_collection()
    aggregator.ZMQ_shutdown()
    if ABORT:
        time.sleep(1)
        return
    time.sleep(20)
    
    #! Done!
    WAIT_FOR_REBOOT = False
    for party in parties:
        party.copy_files(expt)
    for bt in bluetooth_collectors:
        if not bt.copy_files_to_aggregator():
            energy_fl_logger.error(f"Power Collection Failed on {str(bt)}")
            SUCCESS=False
            bt.reboot_collector()
            WAIT_FOR_REBOOT = True
            energy_fl_logger.info(f"Rebooted {str(bt)}")
            paired = False
    #Successful completion validation
    
    if not SUCCESS:
        expt.set_failed()
        energy_fl_logger.error("Experiment Run Failed")
    else:
        expt.set_finished()
    energy_fl_logger.info("Experiment Complete!")
    if WAIT_FOR_REBOOT:
        energy_fl_logger.info("Waiting 1 minute for devices to finish reboot")
        time.sleep(60)
    
completed_experiments = get_completed_experiments(version_str=__version__)
paired = False

for experiment in all_experiments:
    if experiment not in completed_experiments:
        run_experiment(experiment)    
        energy_fl_logger.info("Waiting 60 seconds for next run")
        time.sleep(20)
        energy_fl_logger.info("40 Seconds left")
        time.sleep(30)
        energy_fl_logger.info("10 Seconds left")
        time.sleep(10)
        gc.collect()
    elif run_finished_experiments:
        run_experiment(experiment)
        energy_fl_logger.info("Waiting 60 seconds for next run")
        time.sleep(20)
        energy_fl_logger.info("40 Seconds left")
        time.sleep(30)
        energy_fl_logger.info("10 Seconds left")
        time.sleep(10)
        gc.collect()
