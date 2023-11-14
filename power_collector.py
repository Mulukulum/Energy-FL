"""
on archlinux:
sudo pacman -Sy bluez bluez-firmware bluez-utils bluez-tools python-pybluez
sudo systemctl start bluetooth
sudo bluetoothctl
# power on
# scan on
# pair ###BTADDR###
# trust ###BTADDR###
./um25c_bluetooth_receiver.py ###BTADDR###
{'voltage': 0.496, 'current': 0.17, 'power': 0.843, 'temp_celsius': 28, 'temp_fahrenheit': 82, 'usb_data_pos_voltage': 0.62, 'usb_data_neg_voltage': 0.62, 'charging_mode': 0}
...
"""

import bluetooth
import struct
import time
import threading
import zmq

UM25C_ADDRESS = "98:DA:F0:00:4A:13"
STOP_COLLECTING = False
CONTEXT = zmq.Context()
SOCKET = CONTEXT.socket(zmq.SUB)
SOCKET.connect("tcp://10.8.1.46:6011")
SOCKET.setsockopt(zmq.SUBSCRIBE, b'')

def connect_to_usb_tester(bt_addr):
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((bt_addr, 1))
    sock.settimeout(1.0)
    for _ in range(10):
        try:
            read_data(sock)
        except bluetooth.BluetoothError as e:
            time.sleep(0.2)
        else:
            break
    else:
        raise e
    return sock


def read_data(sock):
    sock.send(bytes([0xF0]))
    d = bytes()
    while len(d) < 130:
        d += sock.recv(1024)
    assert len(d) == 130, len(d)
    return d


def read_measurements(sock):
    d = read_data(sock)
    voltage, current, power = [x / 1000 for x in struct.unpack("!HHI", d[2:10])]
    current = current / 10
    temp_celsius, temp_fahrenheit = struct.unpack("!HH", d[10:14])
    usb_data_pos_voltage, usb_data_neg_voltage = [
        x / 100 for x in struct.unpack("!HH", d[96:100])
    ]
    charging_mode = d[100]
    del d
    del sock
    return locals()


def collect(
    interval: float,
):
    """
    Give the interval in seconds
    """
    import pickle
    from datetime import datetime as dt

    global UM25C_ADDRESS
    global STOP_COLLECTING
    filepath = r"Outputs/Power/Data.pkl"
    sock = connect_to_usb_tester(UM25C_ADDRESS)
    with open(filepath, "wb") as f:
        while STOP_COLLECTING is False:
            measure = read_measurements(sock)
            if isinstance(measure, dict):
                # Add the current time as a timestamp
                timestamp = dt.now().strftime("%H:%M:%S")
                dictionary = {timestamp: measure}
                pickle.dump(dictionary, f)
                time.sleep(interval)
    sock.close()


if __name__ == "__main__":
    import sys

    time.sleep(1)
    try:
        interval = float(sys.argv[1])
    except Exception:
        print("INVALID/NO INTERVAL SPECIFIED, COLLECTING EVERY ONE SECOND")
        interval = 1
    process = threading.Thread(target=collect, args=[interval],)
    process.start()
    SOCKET.recv_pyobj()
    STOP_COLLECTING = True
    print("\nSTOPPING COLLECTION OF POWER DATA\n")
    process.join()
    print("POWER COLLECTION STOPPED...EXITING")
