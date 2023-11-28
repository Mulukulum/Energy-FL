# Energy-FL

### Make sure that the following packages are installed 

```
sudo apt install libbluetooth-dev
sudo apt install expect
sudo apt install sysstat
```

Create a virtual environment

```
python -m venv venv
source venv/bin/activate
```

and pip install the requirements

```
pip install -r requirements.txt
```

All modifications to the flwr folder are marked with 

```
#! ADDED MODIFICATION
```

at both the start and end of the modified code

Ensure that all .sh files have execution permissions when you run the experiment