from ComisCorticalCode import CONFIG, toolbox, CSV
import os
import shutil
from glob import glob


def generate_stages_to_run():
    raise NotImplementedError


def run(sub_dirs):
    #TO DO: take subject loop out of the function for per-job

    run_name = CSV.get_run_name()
    shutil.copyfile('./CONFIG.py', f'./config_files/{run_name}.py')
    CSV.update_new_runs()
    for subject in sub_dirs:
        paths = toolbox.get_paths(subject, run_name)
        for stage in generate_stages_to_run():
            stage.run(paths)
        toolbox.clear_dir(paths['temp'])
    CSV.update_old_runs()
