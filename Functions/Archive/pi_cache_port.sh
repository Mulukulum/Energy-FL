#!/usr/bin/expect

# Define the list of hosts to run the SAR command on
#set hosts [list "10.8.1.35" "10.8.1.200" "10.8.1.158" "10.8.1.207"]
#set hosts [list "10.8.1.35" "10.8.1.207"]

# Define the usernames for each host
#set usernames [list "pi2" "pi3" "pi4" "pi5"]
#set usernames [list "pi2" "pi5"]

# Define ports
#set ports [list "8085" "8086" "8087" "8088"]
#set ports [list "8085" "8086"]
#set password ""

#foreach host $hosts username $usernames port $ports {
#  spawn ssh $username@$host "./Desktop/federated-learning-lib/Functions/clear_cache_port.sh ${port}"
#  expect {
#    "*password*" {
#      send -- "$password\r"
#      exp_continue
#    }
#    eof
#  }
#  puts "Clear cache executed on $host."
#}
