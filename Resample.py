from ComisCorticalCode import Config, toolbox, stage
import nibabel as nb
import numpy as np
import os
import pandas as pd


class Resample(stage.Stage):

    def __init__(self, raw_dat, data, nodif, brain, mask, nthreads, minvol, runs):
        self.raw_mask = os.path.join(raw_dat, 'brain_mask.nii.gz')
        self.raw_data = os.path.join(raw_dat, 'data.nii.gz')
        self.data = data
        self.nodif = nodif
        self.brain = brain
        self.mask = mask
        self.nthreads = nthreads
        self.minvol = minvol

    @staticmethod
    def create_from_dict(paths, config):
        raw_dat = paths["raw_dat"]
        data = paths["data"]
        nodif = paths["nodif"]
        brain = paths['brain']
        mask = paths['mask']
        nthreads = config.nthreads
        minvol = config.minvol
        runs = config.run_list
        return Resample(raw_dat, data, nodif, brain, mask, nthreads, minvol, runs)

    def needed_files(self):
        return [self.data, self.nodif, self.brain, self.mask]

    def parameters_for_comparing_past_runs(self):
        return ['MINVOL']

    def make_commands_for_stage(self):
        mask = nb.load(self.raw_mask).get_data()
        vol = np.sum(mask)

        commands = [
                    toolbox.ExternalCommand.get_command('mrgrid',  self.raw_data, 'regrid', self.data, "-force",
                                                        f'-nthreads {self.nthreads}',
                                                        f'-scale {(self.minvol / vol) ** (1 / 3)}',
                                                        input_files=(self.raw_data,), output_files=(self.data,)),
                    toolbox.ExternalCommand.get_command('fslroi', self.data, self.nodif, 0, 1, input_files=(self.data,),
                                                        output_files=(self.nodif,)),
                    toolbox.ExternalCommand.get_command('bet', self.nodif, self.brain, '-m', '-f 0.2', '-g 0.2',
                                                        input_files=(self.nodif,), output_files=(self.brain, self.mask))
                   ]
        return commands
