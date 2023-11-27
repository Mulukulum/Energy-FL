import subprocess
from common import Experiment
import pathlib


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

    def copy_files(self, exp: Experiment):
        check_if_exists = f"""
if [ -d Outputs/Experiments/{exp.folder_name} ]; then echo 'exists' ; fi ;
"""

        exists = (
            True if str(self.ssh.run([check_if_exists]).stdout) == "exists" else False
        )
        if not exists:
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
            # TODO : Log that the scp failed
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
        self, agg_ip: str, agg_port: int, cid: int, dataset: str, num_parties: int
    ):
        self.ssh.Popen(
            [
                f"python -m clients.scripts.old_client --agg_ip {agg_ip} --agg_port {agg_port} --cid {cid} --dataset {dataset} --client_ip {self.ip} --num_parties {num_parties} --pi_name {self.username} "
            ]
        )
