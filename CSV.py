from ComisCorticalCode import CONFIG
import pandas as pd
import numpy as np


def get_run_name():
    # Random string with the combination of lower and upper case
    runs = pd.read_csv(CONFIG.RUNS, index_col='name')
    name = str(np.max([int(name) for name in runs.index()]) + 1).zfill(5)
    return name


def update_new_runs():
    raise NotImplementedError


def update_old_runs():
    raise NotImplementedError

def find_past_runs(params_to_compare):
    raise NotImplementedError