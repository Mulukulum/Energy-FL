import subprocess
import pathlib
import getpass

list_of_files = [
    "clients/scripts/connect_to_bt_multimeter.sh",
]

THIS_MACHINE_IS_THE_AGGREGATOR = True if getpass.getuser() == "user" else False

USERNAMES_AND_IPS={
    "pi2" : "10.8.1.35",
    "rpi1" : "10.8.1.38",
    "rpi2" : "10.8.1.43",
    "rpi3" : "10.8.1.192",
    "rpi4" : "10.8.1.41"
}

def main():
    for file in list_of_files:
        subprocess.run(f"chmod u+x {file} ; ",shell=True)
    
    if pathlib.Path("clients/scripts/sar_collector.sh").exists():
        subprocess.run(f"chmod u+x clients/scripts/sar_collector.sh", shell=True)
    
    if THIS_MACHINE_IS_THE_AGGREGATOR:
        for username, ip in USERNAMES_AND_IPS.items():
            print(f"\n\n{username}@{ip}\n\n")
            subprocess.run(f"ssh {username}@{ip} << EOF \n cd ~/Energy-FL ; source venv/bin/activate ; python permissions.py ; exit ; \nEOF", shell=True)

if __name__=="__main__":
    main()