cd ~/Desktop/federated-learning-lib
# We can scp the files over to where it belongs now

pi_name=$1
current_ip=$2

scp $pi_name@$current_ip:~/Desktop/federated-learning-lib/Outputs/Evaluations/$pi_name.txt  ./Outputs/Evaluations/$pi_name.txt
scp $pi_name@$current_ip:~/Desktop/federated-learning-lib/Outputs/Evaluations/$pi_name-synced.txt  ./Outputs/Evaluations/$pi_name-synced.txt 
scp $pi_name@$current_ip:~/Desktop/federated-learning-lib/Outputs/$pi_name-epoch-logs.csv  ./Outputs/$pi_name-epoch-logs.csv