
What we need : Anything involving time is never waiting on I/O ops or is slowed down

# Parties must be built to comply with Epoch Logs and Evaluations Storage

## Epoch Logs : 

### CSV file of the format : 

#### Filename : '{PARTY_NAME}-epoch-logs.csv'

##### (RoundNumber, EpochNumber, StartTime, EndTime)


## Model Evaluations:

### .pkl file of the following format : 

#### Filename : '{PARTY_NAME}-evaluations.pkl'

##### Python Dictionary with KEY-VALUE pairs
##### The Key "parser-key" must hold an associated value of a tuple with (RoundNo, EpochNo) if evaluated during training
##### If evaluated in a special evaluation round, "parser-key" must hold a value of a Tuple Containing (-1, -1)

###### Note : Pickle all the dictionaries one by one. It's the server's job to unpickle everything.


# SAR

#### SAR files are already precollected and transferred to the aggregator and put in their respective folders
##### Filenames : '{PARTY_NAME}-sar.txt'


# File Storage

## Power :- Contains Power Data
## Experiments :- Contains Data of all sorts for a given experiment run
## Results :- Contains only the necessary data like graphs, statistics and reports per experiment

### On The Power collectors, files are stored under Outputs/Power with self descriptive names

#### On the RPIs, Data is stored for an experiment in the Experiments Directory, 
#### Everything incl Epoch Logs, SAR and Evaluations are put in the Experiments Directory
##### SAR is temporarily stored in the Outputs/ Folder before being SCP'd to the aggregator. 
##### SAR is given the foldername as an argument which it uses to determine where to SCP the files to

### On The Aggregator all files are stored in Outputs/Experiments with each party getting a folder for itself
#### These folders are the username of the party and contain its epoch-logs and evaluations
#### Additionally each experiment folder will contain a manifest.txt 
#### which lists what files it has and other details regarding the experiment