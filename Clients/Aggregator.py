class Aggregator:
    def __init__(self, ip: str, username: str, flwrPort: int, zmqPort: int) -> None:
        self.ip = ip
        self.username = username
        self.flwrPort = flwrPort
        self.zmqPort = zmqPort

    def __repr__(self) -> str:
        return f"""Aggregator {self.username}@{self.ip} hosting flwr on {self.flwrPort} and broadcasting on {self.zmqPort}"""

    def create_experiment_log(self) -> None:
        #! This assumes that the current working directory is always the ~/Energy-FL/ so that is important to keep in mind
        import pathlib
        if pathlib.Path.exists(r"Outputs/Experiments/log.db"):
            return

        import sqlite3
        con = sqlite3.connect(r"Outputs/Experiments/log.db", detect_types=sqlite3.PARSE_DECLTYPES)
        cur = con.cursor()
        
        cur.execute(f"""CREATE TABLE versions(version_no TEXT PRIMARY KEY, creation_time TEXT NOT NULL)""")
        cur.execute(f"""CREATE TABLE log(expt_id INTEGER PRIMARY KEY, model TEXT NOT NULL, )""")