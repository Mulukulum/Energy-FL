from Clients.Party import sshRunner, Party

class PowerCollector:
    
    def __init__(self, ip: str, username: str, collection_party : Party, bluetooth_address : str, zmq_broadcast_port : int ) -> None:
        self.ip = ip
        self.username = username
        self.ssh = sshRunner(f"{self.username}@{self.ip}")
        self.party = collection_party
        self.tester_address = bluetooth_address 
        self.broadcast_port = zmq_broadcast_port

'''
https://sigrok.org/wiki/RDTech_UM24C

All data returned by the device consists of measurements and configuration status, in 130-byte chunks. To my knowledge, it will never send any other data. All bytes below are displayed in hex format; every command is a single byte.

# Commands to send:
F0 - Request new data dump; this triggers a 130-byte response
F1 - (device control) Go to next screen
F2 - (device control) Rotate screen
F3 - (device control) Switch to next data group
F4 - (device control) Clear data group
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
'''