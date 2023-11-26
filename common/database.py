import sqlite3
import datetime
import pathlib

from .experiments import Experiment


def adapt_and_convert():
    """
    Makes adapters and converters for the following types
    ```
    Experiment ('experiment')
    bool ('bool')
    datetime.datetime ('datetime')

    https://docs.python.org/3/library/sqlite3.html#how-to-write-adaptable-objects
    ```
    """

    def adapt_datetime_iso(val):
        """Adapt datetime.datetime to timezone-naive ISO 8601 date."""
        return val.isoformat()

    sqlite3.register_adapter(datetime.datetime, adapt_datetime_iso)

    def convert_datetime(val):
        """Convert ISO 8601 datetime to datetime.datetime object."""
        return datetime.datetime.fromisoformat(val.decode())

    sqlite3.register_converter("datetime", convert_datetime)

    def adapt_experiment(exp: Experiment):
        #! Edit the cmd_suffixes later
        return f"{exp.version};{exp.model};{exp.fusion};{exp.dataset};{exp.batch_size};{exp.rounds};{exp.epochs};{exp.sample_fraction};{exp.proximal_mu};{exp.num_participating_parties};{exp.run}"

    sqlite3.register_adapter(Experiment, adapt_experiment)

    def convert_experiment(val: str):
        (
            version,
            model,
            fusion,
            dataset,
            batch_size,
            rounds,
            epochs,
            sample_fraction,
            proximal_mu,
            num_parties,
            run,
        ) = val.split(";")
        return Experiment(
            model,
            fusion,
            dataset,
            int(batch_size),
            int(rounds),
            int(epochs),
            float(proximal_mu),
            float(sample_fraction),
            version,
            None if num_parties == "None" else int(num_parties),
            None if run == "None" else int(run),
        )

    sqlite3.register_converter("experiment", convert_experiment)

    def adapt_bool(val: bool) -> int:
        return 1 if val else 0

    sqlite3.register_adapter(bool, adapt_bool)

    def convert_bool(val: int):
        return bool(val)

    sqlite3.register_converter("bool", convert_bool)


def create_experiment_log() -> None:
    #! This assumes that the current working directory is always the ~/Energy-FL/ so that is important to keep in mind

    if pathlib.Path(r"Outputs/Experiments/log.db").exists():
        return

    con = sqlite3.connect(
        r"Outputs/Experiments/log.db", detect_types=sqlite3.PARSE_DECLTYPES
    )
    cur = con.cursor()

    adapt_and_convert()

    cur.execute(
        f"""CREATE TABLE versions(version_no TEXT PRIMARY KEY, creation_time datetime NOT NULL)"""
    )
    cur.execute(
        f"""CREATE TABLE log(expt_id INTEGER PRIMARY KEY, expt experiment NOT NULL, is_finished bool NOT NULL, is_running bool NOT NULL, has_failed bool NOT NULL)"""
    )

    con.commit()
    cur.close()
    con.close()


def get_completed_experiments(version_str : str = None) -> list[Experiment]:
    con = sqlite3.connect(
        r"Outputs/Experiments/log.db", detect_types=sqlite3.PARSE_DECLTYPES
    )
    cur = con.cursor()

    adapt_and_convert()

    if version_str is None:
        cmd_suffix = f""
    else:
        cmd_suffix = f"AND expt LIKE '{version_str};%;%;%;%;%;%;%;%;%;%'"
    
    res = cur.execute(rf"""SELECT expt FROM log WHERE is_finished=1 {cmd_suffix} ;""")
    res = res.fetchall()
    list_of_experiments = [expt[0] for expt in res]

    con.commit()
    cur.close()
    con.close()

    return list_of_experiments


def get_incomplete_experiments(version_str : str = None) -> list[Experiment]:
    con = sqlite3.connect(
        r"Outputs/Experiments/log.db", detect_types=sqlite3.PARSE_DECLTYPES
    )
    cur = con.cursor()

    adapt_and_convert()
    
    if version_str is None:
        cmd_suffix = f""
    else:
        cmd_suffix = f"AND expt LIKE '{version_str};%;%;%;%;%;%;%;%;%;%'"

    res = cur.execute(rf"""SELECT expt FROM log WHERE is_finished=0 {cmd_suffix} ;""")
    res = res.fetchall()
    list_of_experiments = [expt[0] for expt in res]

    con.commit()
    cur.close()
    con.close()

    return list_of_experiments


def get_experiments(version_str : str = None) -> list[Experiment]:
    con = sqlite3.connect(
        r"Outputs/Experiments/log.db", detect_types=sqlite3.PARSE_DECLTYPES
    )
    cur = con.cursor()

    adapt_and_convert()
    
    if version_str is None:
        cmd_suffix = f""
    else:
        cmd_suffix = f"WHERE expt LIKE '{version_str};%;%;%;%;%;%;%;%;%;%'"

    res = cur.execute(rf"""SELECT expt FROM log {cmd_suffix} ;""")
    res = res.fetchall()
    list_of_experiments = [expt[0] for expt in res]

    con.commit()
    cur.close()
    con.close()

    return list_of_experiments


def get_running_experiments(version_str : str = None) -> list[Experiment]:
    con = sqlite3.connect(
        r"Outputs/Experiments/log.db", detect_types=sqlite3.PARSE_DECLTYPES
    )
    cur = con.cursor()

    adapt_and_convert()
    
    if version_str is None:
        cmd_suffix = f""
    else:
        cmd_suffix = f"AND expt LIKE '{version_str};%;%;%;%;%;%;%;%;%;%'"

    res = cur.execute(rf"""SELECT expt FROM log WHERE is_running=1 {cmd_suffix}""")
    res = res.fetchall()
    list_of_experiments = [expt[0] for expt in res]

    con.commit()
    cur.close()
    con.close()

    return list_of_experiments


def get_failed_experiments(version_str : str = None) -> list[Experiment]:
    con = sqlite3.connect(
        r"Outputs/Experiments/log.db", detect_types=sqlite3.PARSE_DECLTYPES
    )
    cur = con.cursor()

    adapt_and_convert()
    
    if version_str is None:
        cmd_suffix = f""
    else:
        cmd_suffix = f"AND expt LIKE '{version_str};%;%;%;%;%;%;%;%;%;%'"

    res = cur.execute(rf"""SELECT expt FROM log WHERE has_failed=1 {cmd_suffix}""")
    res = res.fetchall()
    list_of_experiments = [expt[0] for expt in res]

    con.commit()
    cur.close()
    con.close()

    return list_of_experiments


def nuke_experiments(version_str : str = None):
    con = sqlite3.connect(
        r"Outputs/Experiments/log.db", detect_types=sqlite3.PARSE_DECLTYPES
    )
    cur = con.cursor()
    
    adapt_and_convert()
    
    if version_str is None:
        cmd_suffix = ""
    else:
        cmd_suffix = f"WHERE expt LIKE '{version_str};%;%;%;%;%;%;%;%;%;%'"

    cur.execute(rf"""DELETE FROM log {cmd_suffix} ;""")

    con.commit()
    cur.close()
    con.close()

create_experiment_log()