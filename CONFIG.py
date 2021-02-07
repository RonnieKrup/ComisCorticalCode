from pathlib import Path
import os
import json


class CONFIG:
    def __init__(self):
        self.MINVOL = None    # 259209 for theBase. 577275 for HCP
        self.DATASET_NAME = 'dataset'
        self.DATA_PATH = os.path.join(Path(os.getcwd()).parent, self.DATASET_NAME)
        self.STEPSCALE = 0.5
        self.LENSCALE = (30, 500)
        self.ANGLE = 45
        self.NTRACTS = 5000000
        self.ATLAS = None
        self.ATLAS_META = None
        self.ATLAS_TEMPLATE = None
        self.ATLAS_FOR_CONNECTOME = None
        self.NTHREADS = 2
        self.DATAIN = rf'{self.DATA_PATH}/datain.txt'
        self.INDEX = rf'{self.DATA_PATH}/index.txt'
        self.OUT = os.path.join(Path(os.getcwd()), 'out')
        self.NJOBS = 50

    def to_json(self, json_path):
        data = {key: val for key, val in vars(self).items() if not callable(val)}
        with open(json_path, 'w') as outfile:
            json.dump(data, outfile)

    @staticmethod
    def default_config():
        config = CONFIG()
        return config.check_empty_values_()

    @staticmethod
    def from_json(json_path):
        config = CONFIG()
        with open(json_path) as json_file:
            json_data = json.load(json_file)
        for key, value in json_data.items():
            setattr(config, key, value)
        return config.check_empty_values_()

    def set_value(self, name, val):
        raise NotImplementedError

    def merge_with_parser(self, parser):
        for argname, value in vars(parser).items():
            if not argname == 'config_path':
                setattr(self, argname, value)
        self.check_empty_values_()

    def check_empty_values_(self):
        if not self.MINVOL or not self.ATLAS:
            raise ValueError('must choose minimum brain volume (in voxels) and atlas path')
        if not self.ATLAS_META:
            self.ATLAS_META = self.ATLAS.replace(Path(self.ATLAS).suffix, '.txt')
        if not self.ATLAS_TEMPLATE:
            self.ATLAS_TEMPLATE = "${FSLDIR}/data/standard/MNI152_T1_2mm"
        if not self.ATLAS_FOR_CONNECTOME:
            self.ATLAS_FOR_CONNECTOME = self.ATLAS_META
