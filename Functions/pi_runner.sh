#!/bin/bash

#Initialize all the args

fusion=$1
model=$2
num_parties=$3
dataset=$4
agg_ip=$5
current_ip=$6
agg_broadcast_port=$7
party_listener_port=$8
pi_name=$9
party_id=${10}
datapoints_per_party=${11}


cd ~/Desktop/Energy-FL

#ssh into the pi
ssh -tt $pi_name@$current_ip << EOF
   cd ~/Desktop/Energy-FL;
   source venv/bin/activate;
   scp -r -P222 user@${agg_ip}:~/Desktop/Energy-FL/examples/data/mnist/random/data_party_${party_id}.npz ./examples/data/mnist/random/data_party_${party_id}.npz ;
   python script_pi.py ${fusion} ${model} ${num_parties} ${dataset} ${agg_ip} ${current_ip} ${agg_broadcast_port} ${party_listener_port} ${party_id} ${datapoints_per_party} ;
   mv Outputs/epoch_logs.csv Outputs/$pi_name-epoch-logs.csv
   exit ;
EOF
