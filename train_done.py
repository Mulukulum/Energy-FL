import zmq
import sys
WORK_DONE = 200

_, current_ip, party_listener_port = sys.argv

print(current_ip)
print(party_listener_port)

context = zmq.Context()
sender = context.socket(zmq.PUB)
sender.bind(f"tcp://{current_ip}:{party_listener_port}")
sender.send_pyobj(WORK_DONE)
import time

time.sleep(10)
sender.close()
context.term()
sys.exit()