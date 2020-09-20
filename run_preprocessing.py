import argparse
import time

from ComisCorticalCode import CSV
from subprocess import call


def main():
    parser = make_argument_parser()
    my_vars = get_vars_from_command_line(parser)
    run(my_vars)
    
def run(my_vars):
    # TODO: make all SH files
    sub_dirs = get_sub_dirs(my_vars)
    dump_vars_to_file()
    run_name = CSV.get_run_name()
    CSV.update_new_runs(run_name)

    for subject in sub_dirs:
        while not has_room_for_task():
            time.sleep(60)  # seconds

        # TODO: check if there are N jobs running
        call(f'qsub -N {subject} runQ.sh run_for_sub.py {run_name}')

    # TODO: check done files each X time
    while not finished_tasks():
        time.sleep(60)
    CSV.update_old_runs()


def get_sub_dirs(my_vars):
    raise NotImplementedError


def has_room_for_task():
    raise NotImplementedError


def finished_tasks():
    raise NotImplementedError


def dump_vars_to_file():
    raise NotImplementedError


def make_argument_parser():
    parser = argparse.ArgumentParser("Description of my program goes here")
    parser.add_argument("config_path", type="str")


def get_vars_from_command_line(parser, argv=None):
    parsed_args = parser.parse(argv)
    
    # Lots of ifs
    # If an error, exit
    parser.error("You are stupid")
    # Otherwise, finish building my config and returning it