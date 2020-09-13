import os
from ComisCorticalCode import CONFIG, toolbox, CSV


class Segmentation:
    def __init__(self, mprage, segmentation, mprage2diff, brain, temp, nthreads, raw_dat):
        self.commands = []
        self.env = dict(os.environ)  # Copy the existing environment variables
        self.env['SGE_ROOT'] = ''
        self.mprage_brain = mprage.replace('.nii.gz', 'brain.nii.gz')
        self.segmentation_t1 = os.path.join(raw_dat, 'segmentation_t1.mif')
        self.segmentation = segmentation
        self.mprage2diff = mprage2diff
        self.brain = brain
        self.sgmentation_affine = os.path.join(temp, 'segmentation_affine.txt')
        self.nthreads = nthreads

    @staticmethod
    def create_from_dict(paths):
        mprage = paths['mprage']
        segmentation = paths["5tt"]
        mprage2diff = paths['mprage2diff']
        brain = paths['brain']
        temp = paths['temp']
        nthreads = CONFIG.NTHREADS
        raw_dat = paths['raw_data']
        return Segmentation(mprage, segmentation, mprage2diff, brain, temp, nthreads, raw_dat)

    def run(self):
        if not os.path.isfile(self.segmentation_t1):
            self.segment()
        past_run = CSV.find_past_runs(['MINVOL'])
        if past_run:
            needed_files = (self.segmentation,)
            toolbox.make_link(past_run, needed_files)
        else:
            self.register_segmentation()
        toolbox.run_commands(self.commands)

    def segment(self):
        program_path = '/state/partition1/home/ronniek/mrtrix3/bin/5ttgen'

        self.commands.append(toolbox.get_command(program_path, ('fsl', self.mprage_brain, self.segmentation_t1,
                                                                '-premasked', '-nocrop', '-f')))

    def register_segmentation(self):
        self.commands.append(toolbox.get_command("transformconvert", ("-force", self.mprage2diff, self.mprage_brain,
                                                                      self.brain, 'flirt_import',
                                                                      self.sgmentation_affine)))
        self.commands.append(toolbox.get_command("mrtransform", (self.segmentation_t1, self.segmentation, "-force"),
                                                 nthreads=self.nthreads, linear=self.sgmentation_affine))

