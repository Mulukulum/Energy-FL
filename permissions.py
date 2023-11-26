import subprocess
import pathlib

list_of_files = [
    "clients/scripts/connect_to_bt_multimeter.sh",
]

def main():
    for file in list_of_files:
        subprocess.run(f"chmod u+x {file} ; ",shell=True)
    
    if pathlib.Path("clients/scripts/sar_collector.sh").exists():
        subprocess.run(f"chmod u+x clients/scripts/sar_collector.sh", shell=True)

if __name__=="__main__":
    main()