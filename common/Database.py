import sqlite3
import datetime


def adapt_and_convert():
    """
    Makes adapters and converters for the following types
    ```
    Experiment ('experiment')
    bool ('bool')
    datetime.datetime ('datetime')
    ```
    """
    
    
    from Experiments import Experiment
    
    def adapt_datetime_iso(val):
            """Adapt datetime.datetime to timezone-naive ISO 8601 date."""
            return val.isoformat()

    sqlite3.register_adapter(datetime.datetime, adapt_datetime_iso)
    
    def convert_datetime(val):
        """Convert ISO 8601 datetime to datetime.datetime object."""
        return datetime.datetime.fromisoformat(val.decode())
    
    sqlite3.register_converter("datetime", convert_datetime)
    
    def adapt_experiment(exp : Experiment):
        return f"{exp.version};{exp.model};{exp.fusion};{exp.dataset};{exp.batch_size};{exp.rounds};{exp.epochs};{exp.sample_fraction};{exp.proximal_mu};{exp.num_participating_parties}"
    
    sqlite3.register_adapter(Experiment, adapt_experiment)
    
    def convert_experiment(val : str):
        version, model, fusion, dataset, batch_size, rounds, epochs, sample_fraction, proximal_mu, num_parties = val.split(';')
        return Experiment(model, fusion, dataset, int(batch_size), int(rounds), int(epochs), float(proximal_mu), float(sample_fraction), version, num_parties if num_parties is None else int(num_parties))
    
    sqlite3.register_converter("experiment", convert_experiment)
    
    def adapt_bool(val : bool) -> int:
        return 1 if val else 0
    
    sqlite3.register_adapter(bool, adapt_bool)
    
    def convert_bool(val : int):
        return bool(val)
    
    sqlite3.register_converter("bool", convert_bool)