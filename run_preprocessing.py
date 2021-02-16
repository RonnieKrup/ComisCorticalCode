import argparse
import time
import os
from glob import glob
from ComisCorticalCode import toolbox
from ComisCorticalCode.Config import Config
from subprocess import call
from pathlib import Path
import pandas as pd
import shutil
import sys


def main(argv):
    parser = make_argument_parser()
    config = get_vars_from_command_line(parser, argv)
    run(config)


def run(config):
    sub_dirs = get_sub_dirs(config)

    config.to_json(os.path.join(config.out, 'config_files', config.run_name))
    if config.run_list:
        update_new_runs(config)

    for subject in sub_dirs:
        while not has_room_for_task(config.out, config.njobs, config.run_name):
            time.sleep(60)  # seconds

        job = make_sh_files(subject, config.run_name, config.out)
        call(f'qsub -N {job} {os.path.join(config.out, "sh_files", job)}.sh')

    while not finished_tasks(config.out, run_name=config.run_name, maxjobs=len(sub_dirs)):
        time.sleep(60)
    update_old_runs(config)
    creat_list_of_run_subjects(config.out, config.run_name)
    toolbox.clear_dir(os.path.join(config.out, 'sh_files'))


def make_sh_files(subject_path, run_name, out_path):
    my_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(my_dir, 'send_to_q.sh'), 'r') as f:
        template_file = f.read()
    sub = os.path.split(subject_path)[-1]
    template_file.replace('SCRIPT_TO_RUN', 'run_for_sub.py')
    template_file.replace('SUBJECT_PATH', subject_path)
    template_file.replace('RUN_NAME', run_name)
    template_file.replace('JOB_NAME', sub)
    template_file.replace('OUT_PATH', out_path)
    if sys.prefix == sys.base_prefix:
        venv = ''
    else:
        venv = rf'source {sys.prefix}/bin/activate'
    template_file.replace('VENV_ACTIVATE', venv)


    with open(os.path.join(out_path, 'sh_files', f'{sub}.sh')) as f:
        f.write(template_file)
    return sub


def has_room_for_task(out_path, njobs, run_name):
    running_jobs = glob(os.path.join(out_path, 'jobs', run_name, '*.STARTED'))
    return len(running_jobs) < njobs


def finished_tasks(out_path, maxjobs, run_name):
    done_jobs = glob(os.path.join(out_path, 'jobs', run_name, '*.DONE'))
    return len(done_jobs) >= maxjobs


def creat_list_of_run_subjects(out_path, run_name):
    done_files = glob(os.path.join(out_path, 'jobs', run_name, '*.DONE'))
    done_subs = [Path(sub).stem for sub in done_files]
    with open(os.path.join(out_path, 'subs', f'{run_name}.txt')) as f:
        f.write('\n'.join(done_subs))


def update_new_runs(config):
    shutil.copyfile(config.run_list, config.run_list('.csv', '_new.csv'))
    runs = pd.read_csv(config.run_list.replace('.csv', '_new.csv'))
    vals = ['minvol', 'stepscale', 'lenscale', 'angle', 'ntracts', 'dataset', 'atlas']
    row = pd.Series({v: getattr(config, v) for v in vals}, name=config.run_name)
    runs.append(row)
    runs.to_csv(config.run_list.replace('.csv', '_new.csv'))


def update_old_runs(config):
    # TODO: double check with barak
    shutil.copyfile(config.run_list, config.run_list.replace('.csv', '_old.csv'))
    shutil.copyfile(config.run_list.replace('.csv', '_new.csv'), config.run_list)


def get_sub_dirs(my_vars):
    return glob(os.path.join(my_vars.data_path, '*'))


def make_argument_parser():
    parser = argparse.ArgumentParser("Description of my program goes here")
    parser.add_argument("config_path", type=str, default=None)
    parser.add_argument("minvol", type=int, default=None)
    parser.add_argument("data_path", type=str, default=None)
    parser.add_argument("stepscale", type=float, default=None)
    parser.add_argument("lenscale", type=tuple, default=None)
    parser.add_argument("angle", type=int, default=None)
    parser.add_argument("ntracts", type=int, default=None)
    parser.add_argument("atlas", type=str, default=None)
    parser.add_argument("stlas_meta", type=str, default=None)
    parser.add_argument("atlas_template", type=str, default=None)
    parser.add_argument("atlas_for_connectome", type=str, default=None)
    parser.add_argument("nthreads", type=int, default=None)
    parser.add_argument("datain", type=str, default=None)
    parser.add_argument("index", type=str, default=None)
    parser.add_argument("out", type=str, default=None)
    parser.add_argument("njobs", type=int, default=None)
    parser.add_argument("run_name", type=str, default=None)
    parser.add_argument("run_list", type=str, default=None)
    parser.add_argument("additional_paths", type=list, default=None)

    return parser


def get_vars_from_command_line(parser, argv=None):
    parsed_args = parser.parse_args(argv)
    if parsed_args['config_path']:
        config = Config.from_json(parsed_args['config_path'])
    else:
        config = Config.default_config()
    config.merge_with_parser(parsed_args)
    return config
