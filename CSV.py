from ComisCorticalCode import CONFIG
import pandas as pd
import numpy as np
import os
import shutil


def get_run_name():
    # Random string with the combination of lower and upper case
    runs = pd.read_csv(CONFIG.RUNS, index_col='name')
    name = str(np.max([int(name) for name in runs.index()]) + 1).zfill(5)
    return name


def update_new_runs(name):
    shutil.copyfile(CONFIG.RUNS.replace('.csv', '_new.csv'), CONFIG.RUNS)
    runs = pd.read_csv(CONFIG.RUNS.replace('.csv', '_new.csv'))
    vals = ['MINVOL', 'STEPSCALE', 'LENSCALE', 'ANGLE', 'NTRACTS', 'DATASET', 'ATLAS']
    row = pd.Series({v: eval(f'CONFIG.{v}') for v in vals}, name=name)
    runs.append(row)
    runs.to_csv(CONFIG.RUNS.replace('.csv', '_new.csv'))

def update_old_runs():
    shutil.copyfile(CONFIG.RUNS.replace('.csv', '_new.csv'), CONFIG.RUNS)
    os.rename(CONFIG.RUNS, CONFIG.RUNS.replace('.csv', '_new.csv'))
    os.rename(CONFIG.RUNS.replace('.csv', '_new.csv'), CONFIG.RUNS.replace('.csv', '_old.csv'))


def find_past_runs(params_to_compare):
    runs_path = os.path.join(CONFIG.SUBJECT_HOME, CONFIG.DATASET, 'runs.csv',)
    runs = pd.read_csv(runs_path, index_col='Name')
    relevant_runs = runs
    for param in params_to_compare:
        relevant_runs = relevant_runs[relevant_runs[param] == eval(f'CONFIG.{param}')]
    if len(relevant_runs):
        return relevant_runs.index[0]
    else:
        return None
