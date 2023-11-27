import subprocess
from common import Experiment
import pathlib
from common import energy_fl_logger

class sshRunner:
    """Use this class primarily to run scripts in the clients/scripts/ folder"""

    def __init__(self, ssh_details: str) -> None:
        self.client = ssh_details

    def run(self, cmds: list) -> subprocess.CompletedProcess[bytes]:
        """
        Provide a list with commands terminated by a semicolon, each command is run one after the other on a bash instance on the
        client machine with the energy-FL folder as the present working directory, with the venv activated,
        and it exits automatically after the script ends
        """
        user_cmds = ""
        for cmd in cmds[:-1]:
            user_cmds += f"""{cmd} ; \n    """
        user_cmds += cmds[-1]

        cmd_string = f"""
ssh -tt {self.client} << EOF
    cd ~/Energy-FL;
    source venv/bin/activate;
    {user_cmds}
    exit;
EOF    
"""

        return subprocess.run(cmd_string, shell=True, capture_output=True)

    def Popen(self, cmds: list) -> subprocess.Popen:
        """
        Provide a list with commands terminated by a semicolon, each command is run one after the other on a bash instance on the
        client machine with the energy-FL folder as the present working directory, with the venv activated,
        and it exits automatically after the script ends

        This method exists to run things async, like for example collection of bluetooth data can't be done one by one
        """
        user_cmds = ""
        for cmd in cmds[:-1]:
            user_cmds += f"""{cmd} ; \n    """
        user_cmds += cmds[-1]
        cmd_string = f"""
ssh -tt {self.client} << EOF
    cd ~/Energy-FL;
    source venv/bin/activate;
    {user_cmds}
    exit;
EOF    
"""

        return subprocess.Popen(cmd_string, shell=True)


class Party:
    def __init__(self, ip: str, username: str) -> None:
        self.ip = ip
        self.username = username
        self.ssh = sshRunner(f"{self.username}@{self.ip}")
    
    def __repr__(self) -> str:
        return f"Party {self.username} on {self.ip}"

    def copy_files(self, exp: Experiment):
        import random
        num = random.randint(1042525, 9525765384)
        
        # * The reason I have to do this terribleness is because stdout of the subprocess also gives you all the raspi login text so this is much easier
        check_if_exists = f"""
if [ -d Outputs/Experiments/{exp.folder_name} ]; then echo '{num}' ; fi ;
"""

        exists = (
            True if f"{num}" in str(self.ssh.run([check_if_exists]).stdout.decode()) else False
        )
        if not exists:
            energy_fl_logger.warning(f"Attempted to copy files for {str(self)} but the experiment folder does not exist.")
            return
        
        # Create the folder for the party if it doesn't exist
        pathlib.Path(f"Outputs/Experiments/{exp.folder_name}/{self.username}").mkdir(
            exist_ok=True,
            parents=True,
        )
        # SCP the file over
        res = subprocess.run(
            [
                f"scp -r {self.username}@{self.ip}:~/Energy-FL/Outputs/Experiments/{exp.folder_name} ./Outputs/Experiments/{exp.folder_name}/{self.username}/ "
            ],
            shell=True,
        )
        if res.returncode != 0:
            energy_fl_logger.error(f"Code detects that folder exists on {str(self)} but SCP to aggregator Failed")
            return
        # Extract all the files from said folder incl subfolders and delete the original folder
        subprocess.run(
            [
                f"mv Outputs/Experiments/{exp.folder_name}/{self.username}/* Outputs/Experiments/{exp.folder_name}"
            ],
            shell=True,
        )
        subprocess.run(
            [f"rm -rf Outputs/Experiments/{exp.folder_name}/{self.username}"],
            shell=True,
        )

    def start_client_server(
        self, agg_ip: str, agg_port: int, cid: int, dataset: str, num_parties: int, expt_name : str
    ):
        self.ssh.Popen(
            [
                f"python -m clients.scripts.old_client --agg_ip {agg_ip} --agg_port {agg_port} --cid {cid} --dataset {dataset} --client_ip {self.ip} --num_parties {num_parties} --pi_name {self.username} --expt_name {expt_name} "
            ]
        )
