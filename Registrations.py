from ComisCorticalCode import toolbox, CONFIG, CSV
import os


class Registrations:
    # TODO: Add the '*, ' at the beginning to all other stages - this makes all the parameters keyword-ONLY!
    def __init__(self, *, mprage, temp, brain, mprage2diff, atlas_template, template2mprage, atlas, subject_atlas):
        # TODO: rempve commands from innit in all stages
        self.commands = []
        self.mprage = mprage
        self.mprage_brain = self.mprage.replace('.nii.gz', 'brain.nii.gz')
        self.dif2mprage = os.path.join(temp, 'dif2mprage.mat')
        self.brain = brain
        self.mprage2diff = mprage2diff
        self.atlas_template = atlas_template
        self.mprage2template = os.path.join(temp, 'mprage2template')
        self.template2mprage = template2mprage
        self.atlas = atlas
        self.subject_atlas = subject_atlas

    @staticmethod
    def create_from_dict(paths):
        mprage = paths['mprage']
        temp = paths["temp"]
        brain = paths.brain
        mprage2diff = paths["mprage2diff"]
        atlas_template = CONFIG.ATLAS_TEMPLATE
        template2mprage = paths["template2mprage"]
        atlas = CONFIG.ATLAS
        subject_atlas = paths["atlas"]
        return Registrations(
            mprage=mprage,
            temp=temp,
            brain=brain,
            mprage2diff=mprage2diff,
            atlas_template=atlas_template,
            template2mprage=template2mprage,
            atlas=atlas,
            subject_atlas=subject_atlas)

    def run(self):
        if not os.path.isfile(self.mprage2diff):
            past_run = CSV.find_past_runs(['MINVOL'])
            if past_run:
                needed_files = (self.mprage2diff,)
                toolbox.make_link(past_run, needed_files)
            else:
                self.register_t12diff()
        if not os.path.isfile(self.template2mprage):
            past_run = CSV.find_past_runs(['ATLAS_TEMPLATE'])
            if past_run:
                needed_files = (self.mprage2template,)
                toolbox.make_link(past_run, needed_files)
            else:
                self.register_t12diff()
        if not os.path.isfile(self.atlas):
            past_run = CSV.find_past_runs(['ATLAS_TEMPLATE', 'MINVOL'])
            if past_run:
                needed_files = (self.atlas,)
                toolbox.make_link(past_run, needed_files)
            else:
                self.register_t12diff()
        toolbox.run_commands(self.commands)
    
    # TODO: rename command making functions in all stages
    def register_t12diff(self):
        self.commands.append(toolbox.get_command('bet', (self.mprage, self.mprage_brain, '-m'), f=0.2, g=0.2))

        self.commands.append(toolbox.get_command('flirt', In=self.brain, ref=self.mprage_brain, omat=self.dif2mprage,
                                                 bins=256, cost="normmi", searchrx="-90 90", searchry="-90 90",
                                                 searchrz="-90 90", dof=12))
        self.commands.append(toolbox.get_command("convert_xfm", (self.dif2mprage, "-inverse"), omat=self.mprage2diff))

    def register_template2t1(self):
        self.commands.append(toolbox.get_command("flirt", ref=self.atlas_template, In=self.mprage,
                                                 omat=self.mprage2template))
        self.commands.append(toolbox.get_command("fnirt", In=self.mprage, aff=self.mprage2template,
                                                 ref=self.atlas_template, cout=self.mprage2template,
                                                 config="T1_2_MNI152_2mm"))
        self.commands.append(
            toolbox.get_command('invwarp', ref=self.mprage, out=self.template2mprage, warp=self.mprage2template))

    def register_atlas(self):
        self.commands.append(toolbox.get_command("applywarp", ref=self.mprage, In=self.atlas, out=self.atlas,
                                                 warp=self.template2mprage, interp="nn"))
        self.commands.append(toolbox.get_command("flirt", ("applyxfm",), ref=self.brain, In=self.atlas,
                                                 init=self.mprage2diff, interp="nearestneighbour", out=self.atlas))
