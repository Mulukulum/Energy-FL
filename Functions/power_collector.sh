#!/bin/bash
interval=$1

ssh -tt pi3@10.8.1.200 << EOF
    cd ~/Desktop/Energy-FL;
    source venv/bin/activate;
    python power_collector.py ${interval} ;
    exit ; 
EOF

scp pi3@10.8.1.200:~/Desktop/Energy-FL/Outputs/Power/Data.pkl ./Outputs/Power/Data.pkl