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
            None if num_parties is "None" else int(num_parties),
            None if run is "None" else int(run),
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


def get_completed_experiments() -> list[Experiment]:
    con = sqlite3.connect(
        r"Outputs/Experiments/log.db", detect_types=sqlite3.PARSE_DECLTYPES
    )
    cur = con.cursor()

    adapt_and_convert()

    res = cur.execute(r"""SELECT expt FROM log WHERE is_finished=1 ;""")
    res = res.fetchall()
    list_of_experiments = [expt[0] for expt in res]

    con.commit()
    cur.close()
    con.close()

    return list_of_experiments


def get_incomplete_experiments() -> list[Experiment]:
    con = sqlite3.connect(
        r"Outputs/Experiments/log.db", detect_types=sqlite3.PARSE_DECLTYPES
    )
    cur = con.cursor()

    adapt_and_convert()

    res = cur.execute(r"""SELECT expt FROM log WHERE is_finished=0 ;""")
    res = res.fetchall()
    list_of_experiments = [expt[0] for expt in res]

    con.commit()
    cur.close()
    con.close()

    return list_of_experiments


def get_experiments() -> list[Experiment]:
    con = sqlite3.connect(
        r"Outputs/Experiments/log.db", detect_types=sqlite3.PARSE_DECLTYPES
    )
    cur = con.cursor()

    adapt_and_convert()

    res = cur.execute(r"""SELECT expt FROM log ;""")
    res = res.fetchall()
    list_of_experiments = [expt[0] for expt in res]

    con.commit()
    cur.close()
    con.close()

    return list_of_experiments


def get_running_experiments() -> list[Experiment]:
    con = sqlite3.connect(
        r"Outputs/Experiments/log.db", detect_types=sqlite3.PARSE_DECLTYPES
    )
    cur = con.cursor()

    adapt_and_convert()

    res = cur.execute(r"""SELECT expt FROM log WHERE is_running=1""")
    res = res.fetchall()
    list_of_experiments = [expt[0] for expt in res]

    con.commit()
    cur.close()
    con.close()

    return list_of_experiments


def get_failed_experiments() -> list[Experiment]:
    con = sqlite3.connect(
        r"Outputs/Experiments/log.db", detect_types=sqlite3.PARSE_DECLTYPES
    )
    cur = con.cursor()

    adapt_and_convert()

    res = cur.execute(r"""SELECT expt FROM log WHERE has_failed=1""")
    res = res.fetchall()
    list_of_experiments = [expt[0] for expt in res]

    con.commit()
    cur.close()
    con.close()

    return list_of_experiments


def nuke_experiments():
    con = sqlite3.connect(
        r"Outputs/Experiments/log.db", detect_types=sqlite3.PARSE_DECLTYPES
    )
    cur = con.cursor()

    adapt_and_convert()

    cur.execute(r"""DELETE FROM log""")

    con.commit()
    cur.close()
    con.close()
