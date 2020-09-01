from ComisCorticalCode import CONFIG, toolbox, CSV
import nibabel as nb
import numpy as np
import os
import pandas as pd


class Resample:

    def __init__(self, raw_dat, data, nodif, brain, mask, nthreads, minvol, runs):
        self.commands = []
        self.raw_mask = os.path.join(raw_dat, 'brain_mask.nii.gz')
        self.raw_data = os.path.join(raw_dat, 'data.nii.gz')
        self.data = data
        self.nodif = nodif
        self.brain = brain
        self.mask = mask
        self.nthreads = nthreads
        self.minvol = minvol

    @staticmethod
    def create_from_dict(paths):
        raw_dat = paths["raw_dat"]
        data = paths["data"]
        nodif = paths["nodif"]
        brain = paths['brain']
        mask = paths['mask']
        nthreads = CONFIG.NTHREADS
        minvol = CONFIG.MINVOL
        runs = CONFIG.RUNS
        return Resample(raw_dat, data, nodif, brain, mask, nthreads, minvol, runs)

    def run(self):
        if not os.path.isfile(self.data):
            past_run = CSV.find_past_runs(['MINVOL'])
            if past_run:
                needed_files = [self.data, self.nodif, self.brain, self.mask]
                toolbox.make_link(past_run, needed_files)
            else:
                self.make_resample()
        toolbox.run_commands(self.commands)

    def make_resample(self):
        mask = nb.load(self.raw_mask).get_data()
        vol = np.sum(mask)
        self.commands.append(toolbox.get_command('mrresize', (self.raw_data, self.data, "-force"),
                                                 nthreads=self.nthreads, scale=(self.minvol / vol) ** (1 / 3)))
        self.commands.append(toolbox.get_command('fslroi', (self.data, self.nodif, 0, 1)))
        self.commands.append(toolbox.get_command('bet', (self.nodif, self.brain, '-m'), f=0.2, g=0.2))
