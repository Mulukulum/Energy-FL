import subprocess

class sshRunner:
    """Use this class primarily to run scripts in the Clients/Scripts/ folder"""
    def __init__(self, ssh_details : str) -> None:
        self.client = ssh_details
        
    def run(self, cmds : list) -> None:
        """
        Provide a list with commands, each command is run one after the other on a bash instance on the 
        client machine with the energy-FL folder as the present working directory, with the venv activated, 
        and it exits automatically after the script ends
        """
        
        user_cmds = ""
        for cmd in cmds[:-1]:
            user_cmds+=f'''{cmd} ; \n    '''

        
        
        cmd_string = f"""
ssh -tt {self.client} << EOF
    cd ~/Energy-FL;
    source venv/bin/activate;
    {user_cmds}
    exit;
EOF    
        """
        return subprocess.run(cmd_string, shell=True)
        

class Party:
    
    def __init__(self, ip: str, username: str) -> None:
        self.ip = ip
        self.username = username
        self.ssh = sshRunner(f"{self.username}@{self.ip}")

