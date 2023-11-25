import sqlite3
import pathlib
from common import adapt_and_convert
from common import Experiment

class Aggregator:
    
    def __init__(self, ip: str, username: str, flwrPort: int, zmqPort: int) -> None:
        self.ip = ip
        self.username = username
        self.flwrPort = flwrPort
        self.zmqPort = zmqPort
        self.create_experiment_log()
        
        

    def __repr__(self) -> str:
        return f"""Aggregator {self.username}@{self.ip} hosting flwr on {self.flwrPort} and broadcasting on {self.zmqPort}"""

    @classmethod
    def create_experiment_log(self) -> None:
        #! This assumes that the current working directory is always the ~/Energy-FL/ so that is important to keep in mind
        
        if pathlib.Path.exists(r"Outputs/Experiments/log.db"):
            return
        
        con = sqlite3.connect(r"Outputs/Experiments/log.db", detect_types=sqlite3.PARSE_DECLTYPES)
        cur = con.cursor()
        
        adapt_and_convert()
        
        cur.execute(f"""CREATE TABLE versions(version_no TEXT PRIMARY KEY, creation_time datetime NOT NULL)""")
        cur.execute(f"""CREATE TABLE log(expt_id INTEGER PRIMARY KEY, expt experiment NOT NULL, is_finished bool NOT NULL, is_running bool NOT NULL, has_failed bool NOT NULL)""")
        
        con.commit()
        cur.close()
        con.close()
        
    @classmethod
    def get_completed_experiments(self) -> list[Experiment]:
        
        con = sqlite3.connect(r"Outputs/Experiments/log.db", detect_types=sqlite3.PARSE_DECLTYPES)
        cur = con.cursor()
        
        adapt_and_convert()
        
        res = cur.execute(r"""SELECT expt FROM log WHERE is_finished=1 ;""")
        res = res.fetchall()
        list_of_experiments = [expt[0] for expt in res]
        
        con.commit()
        cur.close()
        con.close()
        
        return list_of_experiments
    
    @classmethod
    def get_incomplete_experiments(self) -> list[Experiment]:
        
        con = sqlite3.connect(r"Outputs/Experiments/log.db", detect_types=sqlite3.PARSE_DECLTYPES)
        cur = con.cursor()
        
        adapt_and_convert()
        
        res = cur.execute(r"""SELECT expt FROM log WHERE is_finished=0 ;""")
        res = res.fetchall()
        list_of_experiments = [expt[0] for expt in res]
        
        con.commit()
        cur.close()
        con.close()
        
        return list_of_experiments

    @classmethod
    def get_experiments(self) -> list[Experiment]:
        
        con = sqlite3.connect(r"Outputs/Experiments/log.db", detect_types=sqlite3.PARSE_DECLTYPES)
        cur = con.cursor()
        
        adapt_and_convert()
        
        res = cur.execute(r"""SELECT expt FROM log ;""")
        res = res.fetchall()
        list_of_experiments = [expt[0] for expt in res]
        
        con.commit()
        cur.close()
        con.close()
        
        return list_of_experiments

    @classmethod
    def get_running_experiments(self) -> list[Experiment]:
        
        con = sqlite3.connect(r"Outputs/Experiments/log.db", detect_types=sqlite3.PARSE_DECLTYPES)
        cur = con.cursor()
        
        adapt_and_convert()
        
        res = cur.execute(r"""SELECT expt FROM log WHERE is_running=1""")
        res = res.fetchall()
        list_of_experiments = [expt[0] for expt in res]
        
        con.commit()
        cur.close()
        con.close()
        
        return list_of_experiments
    
    @classmethod
    def get_failed_experiments(self) -> list[Experiment]:
        
        con = sqlite3.connect(r"Outputs/Experiments/log.db", detect_types=sqlite3.PARSE_DECLTYPES)
        cur = con.cursor()
        
        adapt_and_convert()
        
        res = cur.execute(r"""SELECT expt FROM log WHERE has_failed=1""")
        res = res.fetchall()
        list_of_experiments = [expt[0] for expt in res]
        
        con.commit()
        cur.close()
        con.close()
        
        return list_of_experiments
    
    @classmethod
    def nuke_experiments(self):
        con = sqlite3.connect(r"Outputs/Experiments/log.db", detect_types=sqlite3.PARSE_DECLTYPES)
        cur = con.cursor()
        
        adapt_and_convert()
        
        cur.execute(r"""DELETE FROM log""")
        
        con.commit()
        cur.close()
        con.close()

    def setupZMQ(self):
        import zmq
        self.context = zmq.Context()
        self.broadcast = self.context.socket(zmq.PUB)
        self.broadcast.bind(f"tcp://{self.ip}:{self.zmqPort}")
        
    def zmqStopPowerCollection(self):
        from common import Configuration
        self.broadcast.send_pyobj(Configuration.ZMQ_STOP_POWER_COLLECTION)
        
