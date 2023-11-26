#! This file exists so you can SSH into the aggregator and see what exactly is going on

from clients import Aggregator
from common import adapt_and_convert

Aggregator.create_experiment_log()

adapt_and_convert()


OPT_STRING = """

1. See Running Experiment
2. See Incomplete Experiments
3. See Failed Experiments  
4. Get Completed Experiments
5. Get Incomplete experiments of a particular version
6. Get Failed experiments of a particular version
7. Get Completed experiments of a particular version
8. Delete all experiment logs 
9. Exit

Enter only the number
"""

while True:
    print(OPT_STRING)
    a = input()

    try:
        a = int(a)
    except:
        print("Invalid option entered")
        continue

    if a > 9:
        print("Invalid Option")
        continue

    if a == 1:
        expt = Aggregator.get_running_experiments()
        for i in expt:
            print(i)
    if a == 2:
        expt = Aggregator.get_incomplete_experiments()
        for i in expt:
            print(i)
    if a == 3:
        expt = Aggregator.get_failed_experiments()
        for i in expt:
            print(i)
    if a == 4:
        expt = Aggregator.get_completed_experiments()
        for i in expt:
            print(i)
    if a == 5:
        version = input("Enter version string with prefix. Example 'v1.5'")
        expt = Aggregator.get_incomplete_experiments()
        final = []
        for i in expt:
            if i.version == version:
                final.append(i)
        if final:
            for i in final:
                print(i)
        else:
            print("No Results")
    if a == 6:
        version = input("Enter version string with prefix. Example 'v1.5'")
        expt = Aggregator.get_failed_experiments()
        final = []
        for i in expt:
            if i.version == version:
                final.append(i)
        if final:
            for i in final:
                print(i)
        else:
            print("No Results")
    if a == 7:
        version = input("Enter version string with prefix. Example 'v1.5'")
        expt = Aggregator.get_completed_experiments()
        final = []
        for i in expt:
            if i.version == version:
                final.append(i)
        if final:
            for i in final:
                print(i)
        else:
            print("No Results")

    if a == 8:
        sanity_check = input(
            "Nuking Experiment log can screw up the whole setup if something is running. Type 'Yes' or 'yes' to delete"
        )
        if sanity_check not in ("Yes", "yes"):
            print("Log remains untouched")
            continue
        else:
            Aggregator.nuke_experiments()
            print("Nuked")
    if a == 9:
        break
