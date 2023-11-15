#!/bin/bash

#Initialize all the args

party_id=$1
agg_ip=$2
agg_port=$3
num_parties=$4
dataset=$5
current_ip=$6
pi_name=$7
listener_port=$8

#ssh into the pi
ssh -tt $pi_name@$current_ip << EOF
   cd ~/Desktop/Energy-FL;
   source venv/bin/activate;
   python client.py --cid ${party_id} --dataset ${dataset} --agg_ip ${agg_ip} --agg_port ${agg_port} --num_parties ${num_parties} --client_ip ${current_ip} --pi_name ${pi_name} ;
   mv Outputs/epoch_logs.csv Outputs/$pi_name-epoch-logs.csv ; 
   python train_done.py ${current_ip} ${}
   exit ;
EOF
