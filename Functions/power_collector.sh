#!/bin/bash
interval=$1


ssh -tt pi16@10.8.1.199 << EOF
    cd ~/Desktop/federated-learning-lib;
    source venv/bin/activate;
    python power_collector.py ${interval} ;
    exit ; 
EOF

scp pi16@10.8.1.199:~/Desktop/federated-learning-lib/Outputs/Power/Data.pkl ./Outputs/Power/Data.pkl