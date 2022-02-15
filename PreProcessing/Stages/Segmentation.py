import os
from ComisCorticalCode.PreProcessing import toolbox, stage


class SegmentationStage(stage.Stage):
    def __init__(self, *, mprage, segmentation, mprage2diff, brain, temp, nthreads, raw_dat, minvol):
        self.env = dict(os.environ)  # Copy the existing environment variables
        self.env['SGE_ROOT'] = ''
        self.mprage_brain = mprage.replace('.nii.gz', 'brain.nii.gz')
        self.segmentation_t1 = os.path.join(raw_dat, 'segmentation_t1.mif')
        self.segmentation = segmentation
        self.mprage2diff = mprage2diff
        self.brain = brain
        self.sgmentation_affine = os.path.join(temp, 'segmentation_affine.txt')
        self.nthreads = nthreads
        self.minvol = minvol

    @staticmethod
    def create_from_dict_(cls, paths, config):
        mprage = paths['mprage']
        segmentation = paths["5tt"]
        mprage2diff = paths['mprage2diff']
        brain = paths['brain']
        temp = paths['temp']
        nthreads = config.nthreads
        raw_dat = paths['raw_dat']
        minvol = config.minvol
        return cls(mprage=mprage,
                   segmentation=segmentation, mprage2diff=mprage2diff,
                   brain=brain, temp=temp, nthreads=nthreads, raw_dat=raw_dat, minvol=minvol)


class Segmentation(SegmentationStage):
    def needed_files(self):
        return self.segmentation_t1,

    def parameters_for_comparing_past_runs(self):
        return []

    @staticmethod
    def create_from_dict(paths, config):
        return SegmentationStage.create_from_dict_(Segmentation, paths, config)

    def make_commands_for_stage(self):
        commands = [
            toolbox.ExternalCommand.get_command('5ttgen', 'fsl', self.mprage_brain, self.segmentation_t1,
                                                '-premasked', '-nocrop', '-f', input_files=(self.mprage_brain,),
                                                output_files=(self.segmentation_t1,))
        ]
        return commands


class SegmentRegistration(SegmentationStage):
    def needed_files(self):
        return self.segmentation,

    def parameters_for_comparing_past_runs(self):
        return ['minvol']

    @staticmethod
    def create_from_dict(paths, config):
        return SegmentationStage.create_from_dict_(SegmentRegistration, paths, config)

    def make_commands_for_stage(self):
        commands = [
                    toolbox.ExternalCommand.get_command("transformconvert", "-force", self.mprage2diff,
                                                        self.mprage_brain, self.brain, 'flirt_import',
                                                        self.sgmentation_affine,
                                                        input_files=(self.mprage2diff, self.mprage_brain, self.brain),
                                                        output_files=(self.sgmentation_affine,)),
                    toolbox.ExternalCommand.get_command("mrtransform", self.segmentation_t1, self.segmentation,
                                                        "-force", f'-nthreads {self.nthreads}',
                                                        f'-linear {self.sgmentation_affine}',
                                                        input_files=(self.segmentation_t1, self.sgmentation_affine),
                                                        output_files=(self.segmentation,))
                   ]
        return commands

