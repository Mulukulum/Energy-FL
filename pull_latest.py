import subprocess

USERNAMES_AND_IPS={
    "pi3" : "10.8.1.200",
    "rpi1" : "10.8.1.38",
    "rpi2" : "10.8.1.43",
    "rpi3" : "10.8.1.192",
    "rpi4" : "10.8.1.41"
}

def main():
    subprocess.run('git pull' , shell=True)
    
    for username, ip in USERNAMES_AND_IPS.items():
        subprocess.run(f"ssh {username}@{ip} << EOF \n cd ~/Energy-FL ; git pull ; exit ; \nEOF", shell=True)    

if __name__=="__main__":
    main()