import os
import subprocess

from glob import glob
from pathlib import Path

DRY_RUN = True


class ExternalCommand:
    """
    Wrapper around subprocess.call to create the commandline string and verify input/output file existence.
    """
    def __init__(self, program, *args, input_files=(), output_files=(), **kwargs):
        self.program = program
        self.input_files = input_files
        self.output_files = output_files
        self.args = args
        for arg in args:
            if isinstance(arg, (list, tuple)):
                # TODO: Remove this when all the code works
                raise ValueError(f'Arg {arg} is a list/tuple - did you pass a tuple instead of all the args directly?')
            if not isinstance(arg, (str, int, float)):
                raise ValueError(f'Arg {arg} is not a simple type - Not sure this will convert as expected')
        self.keyword_args = kwargs
        self.command = ""

    @staticmethod
    def get_command(program, *args, input_files=(), output_files=(), **kwargs):
        command = ExternalCommand(program, *args, input_files=input_files, output_files=output_files, **kwargs)
        command.create_command_()
        return command

    def create_command_(self):
        result = [self.program]
        for arg in self.args:
            result.append(str(arg))
        for arg_name, arg_value in self.keyword_args.items():
            result.append(f'--{arg_name.lower()}={arg_value}')
        self.command = " ".join(result)

    @staticmethod
    def find_missing_files(paths):
        """Returns which files do not exist"""
        return [path for path in paths if not os.path.isfile(path)]

    def check_input_files_exist(self):
        """Raise an exception if input files are missing"""
        missing = self.find_missing_files(self.input_files)
        if missing:
            raise FileNotFoundError(f'Missing input files {missing}')

    def check_output_files_exist(self):
        """Raise an exception if output files are missing"""
        missing = self.find_missing_files(self.output_files)
        if missing:
            raise FileNotFoundError(f'Missing output files {missing}')

    def run_command(self, environment=None):
        """Runs the command, raises an exception on missing input/output fails or failed command."""
        print(self.command)
        if DRY_RUN:
            print(f'this is a dry run. {self.program} not run and input/output files not checked.')
            return

        self.check_input_files_exist()
        # Raises an error if the command has a non-zero exit code
        subprocess.check_call(self.command, shell=True, env=(environment or os.environ))
        self.check_output_files_exist()


def clear_dir(path):
    """Removes all files in a directory."""
    if DRY_RUN:
        print(f"this is a dry run. folder {path} not cleared.")
        return
    for f in glob(f'{path}/*'):
        os.remove(f)


def make_link(past_run_name, files_to_link):
    """For every file in files_to_link, link to a file with the same suffix and path but named as `past_run`"""
    # TODO: Create better documentation
    # WARNING WARNING WARNING - THIS MIGHT NOT DO WHAT YOU EXPECT
    for new_file in files_to_link:
        path = Path(new_file)
        old_file = files_to_link.replace(path.stem, past_run_name)
        if not DRY_RUN:
            os.link(old_file, new_file)
        else:
            print(f'Would link {old_file} as {new_file}')


def get_paths(base_dir, name):
    local_paths = {
        'raw_dat': 'raw_data/',
        'temp': f'temp_{name}/',
        'bvecs': 'raw_data/bvecs',
        'bvals': 'raw_data/bvals',
        'mprage': r'raw_data/mprage.nii.gz',
        "mprage2diff": rf'reg_t12dif/{name}.mat',
        "template2mprage": rf'reg_template2t1/{name}.nii.gz',
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
    global_paths = {
        name: os.path.join(base_dir, value)
        for name, value in local_paths.items()
    }
    for path in list(global_paths.values()):
        if not os.path.isdir(os.path.split(path)[0]):
            os.mkdir(os.path.split(path)[0])
    return global_paths






