from pathlib import Path
import os
import json
import numpy as np
import pandas as pd


class Config:
    def __init__(self):
        self.minvol = None    # 259209 for theBase. 577275 for HCP
        self.dataset_name = 'dataset'
        self.data_path = os.path.join(Path(os.getcwd()).parent, self.dataset_name)
        self.stepscale = 0.5
        self.lenscale = (30, 500)
        self.angle = 45
        self.ntracts = 5000000
        self.atlas = None
        self.atlas_meta = None
        self.atlas_template = None
        self.atlas_for_connectome = None
        self.nthreads = 2
        self.datain = rf'{self.data_path}/datain.txt'
        self.index = rf'{self.data_path}/index.txt'
        self.out = os.path.join(Path(os.getcwd()), 'out')
        self.njobs = 1
        self.run_name = None
        self.run_list = None
        self.additional_paths = []

    def to_json(self, json_path):
        data = {key: val for key, val in vars(self).items() if not callable(val)}
        with open(json_path, 'w') as outfile:
            json.dump(data, outfile)

    @staticmethod
    def from_json(json_path):
        config = Config()
        with open(json_path) as json_file:
            json_data = json.load(json_file)
        for key, value in json_data.items():
            setattr(config, key, value)
        return config

    def set_value(self, name, val):
        raise NotImplementedError

    def merge_with_parser(self, parser):
        for argname, value in vars(parser).items():
            if not argname == 'config_path':
                setattr(self, argname, value)
        self.validate_config_values()

    def get_run_name(self):
        # Random string with the combination of lower and upper case
        runs = pd.read_csv(self.run_list, index_col='run_name')
        if len(runs.index) == 0:
            self.run_name = 'run_00001'
        else:
            self.run_name = 'run_' + str(np.max([int(name.split('_')[-1]) for name in runs.index]) + 1).zfill(5)

    def validate_config_values(self):
        if not self.minvol or not self.atlas:
            # TODO: this might always raise an error
            raise ValueError('must choose minimum brain volume (in voxels) and atlas path')
        if not self.atlas_meta:
            self.atlas_meta = self.atlas.replace(Path(self.atlas).suffix, '.txt')
            print('no atlas metadata specified. used {atlas}.txt')
        if not self.atlas_template:
            self.atlas_template = "${FSLDIR}/data/standard/MNI152_T1_2mm"
            print('no atlas template specified. used MNI 2mm')
        if not self.atlas_for_connectome:
            print('no atlas for connectome specified. used same atlas')
        if not self. run_name:
            if self.run_list:
                if os.path.isfile(self.run_list):
                    self.get_run_name()
                else:
                    self.run_name = 'run_00001'
                    vals = ['run_name', 'minvol', 'stepscale', 'lenscale', 'angle', 'ntracts', 'dataset_name', 'atlas']
                    run_list = pd.DataFrame(columns=vals)
                    run_list = run_list.set_index('run_name')
                    run_list.to_csv(self.run_list)
            else:
                self.run_name = 'test'
                print('no run name was specified. run named "test"')
        out_dirs = ['config_files', 'sh_files', self.run_name]
        for d in out_dirs:
            os.makedirs(os.path.join(self.out, d), exist_ok=True)
