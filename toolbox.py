import os
from subprocess import call
from glob import glob
from pathlib import Path

DRY_RUN = False


# TODO: Consider wrapping commands with this, so that we can check that all files are there, and not just check
# the return code. (Callers to get_command will need to specify the input and output files)
class ExternalToolExecution:
    def __init__(self, program, input_files=(), output_files=(), args=(), **kwargs):
        self.program = program
        self.input_files = input_files
        self.output_files = output_files
        self.args = args
        self.keyword_args = kwargs
        self.command = ""

    @staticmethod
    def get_command(program, input_files=(), output_files=(), args=(), **kwargs):
        command = ExternalToolExecution(program, input_files, output_files, args, **kwargs)
        command.create_command()
        return command

    def create_command(self):
        result = [self.program]
        for arg in self.args:
            result.append(arg)
        for arg_name, arg_value in self.keyword_args.items():
            result.append(f'--{arg_name.lower()}={arg_value}')
        self.command = " ".join(result)

    def run_command(self, environment):
        print(self.command)
        if not DRY_RUN:
            exit_code = call(self.command, shell=True, env=environment)
        else:
            exit_code = 0
            print(f'this is a dry run. {self.program} not run.')
        if exit_code != 0:
            return False



def clear_dir(path):
    if not DRY_RUN:
        for f in glob(f'{path}/*'):
            os.remove(f)
    else:
        print(f"this is a dry run. folder {path} not cleared.")


def find_file_name(names, base_path):
    for path in names:
        if os.path.isfile(os.path.join(base_path, path)):
            return path
    return None


def get_command(program, args=(), **kwargs):
    result = [program]
    for arg in args:
        result.append(arg)
    for arg_name, arg_value in kwargs.items():
        result.append(f'--{arg_name.lower()}={arg_value}')
    return ' '.join(result)


def make_link(past_run, files_to_link):
    for new_file in files_to_link:
        path = Path(new_file)
        old_file = files_to_link.replace(path.stem, past_run)
        if not DRY_RUN:
            os.link(old_file, new_file)
        else:
            print(old_file, new_file)


def get_paths(base_dir, name):
    local_paths = {
        'raw_dat': 'raw_data/data.nii.gz',
        'temp': 'temp_{name}/',
        'bvecs': 'raw_data/bvecs',
        'bvals': 'raw_data/bvals',
        'mprage': r'raw_data/mprage.nii.gz',
        "mprage2diff": rf'affine/t12dif/{name}.mat',
        "template2mprage": rf'affine/template2t1/{name}.mat',
        "5tt": fr'5tt/{name}.mif',
        'data': rf'data/{name}.nii.gz',
        'nodif': rf'nodif/{name}.nii.gz',
        'brain': rf'brain/{name}.nii.gz',
        'mask': rf'brain/{name}_mask.nii.gz',
        'atlas': rf'atlas/{name}.nii.gz',
        "res": rf'wm_res/{name}.txt',
        "fod": rf'wm_fod/{name}.mif',
        'tracts': rf'tracts_unsifted/{name}.tck',
        'sifted_tracts': f'tracts/{name}.tck',
        'tracts_atlas': f'temp_{name}/atlas_tracts_unsifted.tck',
        'sifted_atlas_tracts': f'atlas_tracts/{name}.tck'
    }

    return {
        name: os.path.join(base_dir, value)
        for name, value in local_paths.items()
    }







