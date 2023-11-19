# Client Identification

Clients need to be uniquely identifiable by the aggregator.

IP uniquely identifies each client

Ideally, a client class should exist with methods to :

    - Copy the Files for a certain set of experiments
    - Participate in an FL experiment.
    - Check what experiments have run on it

Parties don't need an experiment log since we already maintain one on the aggregator. 
Logging to plain text about start and stop should be sufficient.

It should be sufficient if we just have the functionality to copy files for experiments.
SAR data-collection can happen using existing scripts.

Power collection requires another class with functionality.