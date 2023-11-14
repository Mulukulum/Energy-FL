#!/bin/bash

#Initialize all the args

num_parties=$1
dataset=$2
agg_ip=$3
current_ip=$4
agg_broadcast_port=$5
party_listener_port=$6
pi_name=$7
party_id=$8

#ssh into the pi
ssh -tt $pi_name@$current_ip << EOF
   cd ~/Desktop/Energy-FL;
   source venv/bin/activate;
   scp -r -P222 user@${agg_ip}:~/Desktop/Energy-FL/examples/data/mnist/random/data_party_${party_id}.npz ./examples/data/mnist/random/data_party_${party_id}.npz ;
   python script_pi.py ${num_parties} ${dataset} ${agg_ip} ${current_ip} ${agg_broadcast_port} ${party_listener_port} ${party_id} ${datapoints_per_party} ;
   mv Outputs/epoch_logs.csv Outputs/$pi_name-epoch-logs.csv
   exit ;
EOF
