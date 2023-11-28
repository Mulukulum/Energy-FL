# This script is for collecting power data from the Multimeters

CLEAR_DATA_GROUP = 0xF4
REQUEST_DATA_DUMP = 0xF0
SET_DATA_GROUP_FIVE = 0xA5
DIM_SCREEN = 0xD0
SET_SCREENSAVER = 0xE1

STOP_POWER_COLLECTION = 300
STOP_COLLECTING = False

import bluetooth
import struct
import time
import threading
import zmq
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--zmq_ip", help="ZMQ Port that aggregator is broadcasting on", type=str
)
parser.add_argument("--address", help="Address of the bluetooth multimeter", type=str)
parser.add_argument("--filename", help="Filename of the pkl file", type=str)
args = parser.parse_args()

ZMQ_BROADCAST_ADDRESS, UM25C_ADDRESS, name = args.zmq_ip, args.address, args.filename


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
    sock.send(bytes([REQUEST_DATA_DUMP]))
    d = bytes()
    while len(d) < 130:
        d += sock.recv(1024)
    assert len(d) == 130, len(d)
    return d


def set_initial_parameters(sock):
    sock.send(bytes([SET_DATA_GROUP_FIVE]))
    time.sleep(0.1)
    sock.send(bytes([SET_SCREENSAVER]))
    time.sleep(0.1)
    sock.send(bytes([DIM_SCREEN]))
    time.sleep(0.1)
    sock.send(bytes([CLEAR_DATA_GROUP]))


def read_measurements(sock):
    d = read_data(sock)
    voltage, current, power = [x / 1000 for x in struct.unpack("!HHI", d[2:10])]
    current = current / 10
    mAh, mWh = [x for x in struct.unpack("!II", d[102:110])]
    return {
        "voltage": voltage,
        "current": current,
        "power": power,
        "mAh": mAh,
        "mWh": mWh,
    }


def collect(
    interval: float,
):
    import pickle
    from datetime import datetime as dt

    global UM25C_ADDRESS
    global STOP_COLLECTING

    filepath = f"Outputs/Power/{name}.pkl"
    sock = connect_to_usb_tester(UM25C_ADDRESS)
    fail_count = 0
    with open(filepath, "wb") as f:
        set_initial_parameters(sock)
        while True:
            try:
                d = read_measurements(sock)
            except bluetooth.BluetoothError:
                time.sleep(0.1)
                fail_count+=1
                if fail_count == 10 : print("10 Failures reached")
                continue
            # Time with seconds to 3 decimal points
            now = dt.now().strftime(r"%H:%M:%S.%f")[:-3]
            pickle.dump((now, d), f)
            if STOP_COLLECTING:
                break
            time.sleep(interval)

    sock.close()


def wait_until_ready(value, SOCKET) -> None:
    finished = False
    while finished is False:
        try:
            response = SOCKET.recv_pyobj(flags=zmq.NOBLOCK)
        except zmq.ZMQError:
            ...
        else:
            if response == value:
                finished = True
                return
            else:
                time.sleep(3)


CONTEXT = zmq.Context()
SOCKET = CONTEXT.socket(zmq.SUB)
SOCKET.connect(f"tcp://{ZMQ_BROADCAST_ADDRESS}")
SOCKET.setsockopt(zmq.SUBSCRIBE, b"")

interval = 0.25
thread = threading.Thread(
    target=collect,
    args=[interval],
)
thread.start()
wait_until_ready(STOP_POWER_COLLECTION, SOCKET)
STOP_COLLECTING = True
thread.join()

"""
https://sigrok.org/wiki/RDTech_UM24C

All data returned by the device consists of measurements and configuration status, in 130-byte chunks. To my knowledge, it will never send any other data. All bytes below are displayed in hex format; every command is a single byte.

# Commands to send:
F0 - Request new data dump; this triggers a 130-byte response
F1 - (device control) Go to next screen
F2 - (device control) Rotate screen
F3 - (device control) Go to the previous screen
F4 - (device control) Clear data group
Ax - (device control) Set the selected data group (0-9)
Bx - (configuration) Set recording threshold to a value between 0.00 and 0.15 A (where 'x' in the byte is 4 bits representing the value after the decimal point, eg. B7 to set it to 0.07 A)
Cx - (configuration) Same as Bx, but for when you want to set it to a value between 0.16 and 0.30 A (16 subtracted from the value behind the decimal point, eg. 0.19 A == C3)
Dx - (configuration) Set device backlight level; 'x' must be between 0 and 5 (inclusive)
Ex - (configuration) Set screen timeout ('screensaver'); 'x' is in minutes and must be between 0 and 9 (inclusive), where 0 disables the screensaver

# Response format:
All byte offsets are in decimal, and inclusive. All values are big-endian and unsigned.
0   - 1   Start marker (always 0x0963)
2   - 3   Voltage (in mV, divide by 1000 to get V)
4   - 5   Amperage (in mA, divide by 1000 to get A)
6   - 9   Wattage (in mW, divide by 1000 to get W)
10  - 11  Temperature (in celsius)
12  - 13  Temperature (in fahrenheit)
14        Unknown (not used in app)
15        Currently selected data group
16  - 95  Array of main capacity data groups (where the first one, group 0, is the ephemeral one)
            -- for each data group: 4 bytes mAh, 4 bytes mWh
96  - 97  USB data line voltage (positive) in centivolts (divide by 100 to get V)
98  - 99  USB data line voltage (negative) in centivolts (divide by 100 to get V)
100       Charging mode; this is an enum, where 0 = unknown/standard, 1 = QC2.0, and presumably 2 = QC3.0 (but I haven't verified this)
101       Unknown (not used in app)
102 - 105 mAh from threshold-based recording
106 - 109 mWh from threshold-based recording
110 - 111 Currently configured threshold for recording
112 - 115 Duration of recording, in seconds since start
116       Recording active (1 if recording)
117       Unknown (not used in app)
118 - 119 Current screen timeout setting
120 - 121 Current backlight setting
122 - 125 Resistance in deci-ohms (divide by 10 to get ohms)
126       Unknown
127       Current screen (same order as on device)
128 - 129 Stop marker (always 0xfff1)

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
