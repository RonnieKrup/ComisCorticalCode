import argparse
import time
import os
from glob import glob
from ComisCorticalCode.PreProcessing import toolbox
from ComisCorticalCode.PreProcessing.Config import Config
from subprocess import call
from shutil import which
from pathlib import Path
import pandas as pd
import shutil
import sys
from multiprocessing import Pool


class Runner:
    def run_all_subjects(self, config, sub_dirs, out):
        raise NotImplementedError()


class QsubRunner(Runner):
    def run_all_subjects(self, config, sub_dirs, out):
        sh_files = make_multiple_sh_files(sub_dirs, config.run_name, config.out)
        run_all_batch_tasks(sh_files, config)
        toolbox.clear_dir(os.path.join(config.out, 'sh_files'))


class LocalRunnerWithShellScripts(Runner):
    def run_all_subjects(self, config, sub_dirs, out):
        sh_files = make_multiple_sh_files(sub_dirs, config.run_name, config.out)
        run_all_tasks(sh_files, config)
        toolbox.clear_dir(os.path.join(config.out, 'sh_files'))


def run_with_config_and_runner(config, runner: Runner):
    sub_dirs = get_sub_dirs(config)
    make_dirs(config)
    config.to_json(os.path.join(config.out, 'config_files', config.run_name + ".json"))
    if config.run_list:
        create_new_runs_file(config)
        update_current_runs_to_new(config)
    runner.run_all_subjects(config, sub_dirs, config.out)
    creat_list_of_run_subjects(config.out, config.run_name)


def run(argv):
    parser = make_argument_parser()
    config = get_vars_from_command_line(parser, argv)
    if check_if_qsub_available():
        run_with_config_and_runner(config, QsubRunner())
    else:
        run_with_config_and_runner(config, LocalRunnerWithShellScripts())


def make_dirs(config):
    out_dirs = ['config_files', 'jobs', 'sh_files', 'subs']
    for d in out_dirs:
        os.makedirs(os.path.join(config.out, d), exist_ok=True)


def check_if_qsub_available():
    return which('qsub') is not None

# TODO: 2. Run the sh file for a new candidate and make sure it works for that single subject
# TODO: 4.


def run_batch_task(script_path): # tested, TODO: waiting for barak
    job_name = Path(script_path).stem
    call(f'qsub -N {job_name} {script_path}')


def run_single_task(script_path, out):# TODO: ask barak if I can do this without the SH file (and still have a log)
    call(f'bash {script_path} > {os.path.join(out, "qstOut")}')


def run_all_batch_tasks(sh_files, config):
    for script_path in sh_files:
        while not has_room_for_task(config.out, config.njobs, config.run_name):
            time.sleep(60)  # seconds
        run_batch_task(script_path)
    while not finished_tasks(config.out, run_name=config.run_name, maxjobs=len(sh_files)):
        time.sleep(60)


def run_all_tasks(sh_files, config):
    with Pool(processes=config.njobs) as pool:
        pool.map(run_single_task, sh_files)


def make_multiple_sh_files(sub_dirs, run_name, out): # tested
    return [make_sh_file(sub_dir, run_name, out) for sub_dir in sub_dirs]


def make_sh_file(subject_path, run_name, out_path): # tested
    my_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(my_dir, '../template_files/send_to_q.sh'), 'r') as f:
        template_file = f.read()
    sub = os.path.split(subject_path)[-1]
    out_sh = os.path.join(out_path, 'sh_files', f'{sub}.sh')
    template_file = template_file.replace('SCRIPT_TO_RUN', os.path.join(my_dir, 'run_for_sub.py'))
    template_file = template_file.replace('MY_DIR', my_dir)
    template_file = template_file.replace('SUBJECT_PATH', subject_path)
    template_file = template_file.replace('RUN_NAME', run_name)
    template_file = template_file.replace('JOB_NAME', sub)
    template_file = template_file.replace('OUT_PATH', out_path)
    if sys.prefix == sys.base_prefix:
        venv = ''
    else:
        venv = rf'source {sys.prefix}/bin/activate'
    template_file = template_file.replace('VENV_ACTIVATE', venv)

    with open(out_sh, 'w') as f:
        f.write(template_file)
    return out_sh


def has_room_for_task(out_path, njobs, run_name):
    running_jobs = glob(os.path.join(out_path, 'jobs', run_name, '*.STARTED'))
    return len(running_jobs) < njobs


def finished_tasks(out_path, maxjobs, run_name):
    done_jobs = glob(os.path.join(out_path, 'jobs', run_name, '*.DONE'))
    return len(done_jobs) >= maxjobs


def creat_list_of_run_subjects(out_path, run_name): # tested
    done_files = glob(os.path.join(out_path, 'jobs', run_name, '*.DONE'))
    done_subs = [Path(sub).stem for sub in done_files]
    list_path = os.path.join(out_path, 'subs', f'{run_name}.txt')
    with open(list_path, 'w') as f:
        f.write('\n'.join(done_subs))


def create_new_runs_file(config): # tested
    existing_file_name = config.run_list
    new_file_name = config.run_list.replace('.csv', '_new.csv')
    runs = pd.read_csv(existing_file_name)
    runs = runs.set_index('run_name')
    vals = ['run_name', 'minvol', 'stepscale', 'lenscale', 'angle', 'ntracts', 'dataset_name', 'atlas']
    row = pd.Series({v: getattr(config, v) for v in vals}, name=config.run_name)
    runs = runs.append(row)
    runs.to_csv(new_file_name)


def update_current_runs_to_new(config): # tested
    shutil.copyfile(config.run_list, config.run_list.replace('.csv', '_old.csv'))
    shutil.move(config.run_list.replace('.csv', '_new.csv'), config.run_list)


def get_sub_dirs(my_vars):
    return glob(os.path.join(my_vars.data_path, '*'))


def make_argument_parser():
    parser = argparse.ArgumentParser("Description of my program goes here")
    parser.add_argument("config_path", type=str, default=None)
    parser.add_argument("minvol", type=int, default=None)
    parser.add_argument("data_path", type=str, default=None)
    parser.add_argument("stepscale", type=float, default=None)
    parser.add_argument("lenscale_min", type=int, default=None)
    parser.add_argument("lenscale_max", type=int, default=None)
    parser.add_argument("angle", type=int, default=None)
    parser.add_argument("ntracts", type=int, default=None)
    parser.add_argument("atlas", type=str, default=None)
    parser.add_argument("atlas_meta", type=str, default=None)
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
        config = Config()
    config.merge_with_parser(parsed_args)
    return config
