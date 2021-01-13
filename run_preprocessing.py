import argparse
import time
import os
from glob import glob

from ComisCorticalCode import CSV, toolbox
from ComisCorticalCode.CONFIG import CONFIG
from subprocess import call
from pathlib import Path


def main():
    parser = make_argument_parser()
    config = get_vars_from_command_line(parser)
    run(config)


def run(config):
    sub_dirs = get_sub_dirs(config)
    out_path = config.OUT
    run_name = CSV.get_run_name()

    config.to_json(os.path.join(out_path, 'config_files', run_name))
    CSV.update_new_runs(run_name)

    for subject in sub_dirs:
        while not has_room_for_task(out_path, config.NJOBS, run_name):
            time.sleep(60)  # seconds

        job = make_sh_files(subject, run_name, out_path)
        call(f'qsub -N {job} {job}.sh')

    while not finished_tasks(out_path, run_name=run_name, njobs=len(sub_dirs)):
        time.sleep(60)
    CSV.update_old_runs()
    creat_list_of_run_subjects(out_path)
    toolbox.clear_dir(os.path.join(out_path, 'sh_files'))


def make_sh_files(subject_path, run_name, out_path):
    with open('send_to_q.sh', 'r') as f:
        template_file = f.read()
    sub = os.path.split(subject_path)[-1]
    template_file.replace('SCRIPT_TO_RUN', 'run_for_sub.py')
    template_file.replace('SUBJECT_PATH', subject_path)
    template_file.replace('RUN_NAME', run_name)
    template_file.replace('JOB_NAME', sub)
    template_file.replace('OUT_PATH', out_path)

    with open(os.path.join(out_path, 'sh_files', f'{sub}.sh')) as f:
        f.write(template_file)
    return sub


def has_room_for_task(out_path, njobs, run_name):
    running_jobs = glob(os.path.join(out_path, 'jobs', run_name, '*.STARTED'))
    return len(running_jobs) < njobs


def finished_tasks(out_path, njobs, run_name):
    done_jobs = glob(os.path.join(out_path, 'jobs', run_name, '*.DONE'))
    return len(done_jobs) >= njobs


def creat_list_of_run_subjects(out_path, run_name):
    done_files = glob(os.path.join(out_path, 'jobs', run_name, '*.DONE'))
    done_subs = [Path(sub).stem for sub in done_files]
    with open(os.path.join(out_path, 'subs', f'{run_name}.txt')) as f:
        f.write('\n'.join(done_subs))


def get_sub_dirs(my_vars):
    return glob(os.path.join(my_vars['DATA_PATH'], '*'))


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

    return parser


def get_vars_from_command_line(parser, argv=None):
    parsed_args = parser.parse_args(argv)
    if parsed_args['config_path']:
        config = CONFIG.from_json(parsed_args['config_path'])
    else:
        config = CONFIG.default_config()
    config.merge_with_parser(parsed_args)
    return config
