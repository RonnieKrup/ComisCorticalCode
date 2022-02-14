from ComisCorticalCode import toolbox, stage
import os


class RegistrationStage(stage.Stage):
    def __init__(self, *, mprage, temp, brain, mprage2diff, atlas_template, template2mprage, sub_atlas, atlas,
                 subject_atlas, minvol):
        self.mprage = mprage
        self.mprage_brain = self.mprage.replace('.nii.gz', 'brain.nii.gz')
        self.dif2mprage = os.path.join(temp, 'dif2mprage.mat')
        self.brain = brain
        self.mprage2diff = mprage2diff
        self.atlas_template = atlas_template
        self.mprage2template = os.path.join(temp, 'mprage2template')
        self.template2mprage = template2mprage
        self.sub_atlas = sub_atlas
        self.atlas = atlas
        self.subject_atlas = subject_atlas
        self.minvol = minvol

    @staticmethod
    def create_from_dict_(cls, paths, config):
        # cls is the class to create
        mprage = paths['mprage']
        temp = paths["temp"]
        brain = paths['brain']
        mprage2diff = paths["mprage2diff"]
        atlas_template = config.atlas_template
        template2mprage = paths["template2mprage"]
        sub_atlas = paths['atlas']
        subject_atlas = paths["atlas"]
        atlas = config.atlas
        minvol = config.minvol
        return cls(
            mprage=mprage,
            temp=temp,
            brain=brain,
            mprage2diff=mprage2diff,
            atlas_template=atlas_template,
            template2mprage=template2mprage,
            sub_atlas=sub_atlas,
            subject_atlas=subject_atlas,
            atlas=atlas,
            minvol=minvol)


class RegistrationT12diff(RegistrationStage):
    PARAMETERS = ['minvol']

    @staticmethod
    def create_from_dict(paths, config):
        return RegistrationStage.create_from_dict_(RegistrationT12diff, paths, config)

    def needed_files(self):
        return self.mprage2diff,

    def parameters_for_comparing_past_runs(self):
        return self.PARAMETERS

    def make_commands_for_stage(self):
        commands = [
                    toolbox.ExternalCommand.get_command('bet', self.mprage, self.mprage_brain, '-m', '-f 0.2', '-g 0.2',
                                                        input_files=(self.mprage,),
                                                        output_files=(self.mprage_brain,)),
                    toolbox.ExternalCommand.get_command('flirt', f'-in {self.brain}', f'-ref {self.mprage_brain}',
                                                        f'-omat {self.dif2mprage}', '-bins 256', '-cost normmi',
                                                        '-searchrx -90 90', '-searchry -90 90', '-searchrz -90 90',
                                                        '-dof 12', output_files=(self.dif2mprage,),
                                                        input_files=(self.brain, self.mprage_brain)),
                    toolbox.ExternalCommand.get_command("convert_xfm", self.dif2mprage, "-inverse",
                                                        f'-omat {self.mprage2diff}', input_files=(self.dif2mprage,),
                                                        output_files=(self.mprage2diff,))
                    ]
        return commands


class RegistrationTemplate2t1(RegistrationStage):
    PARAMETERS = ['atlas_template'] + RegistrationT12diff.PARAMETERS

    @staticmethod
    def create_from_dict(paths, config):
        return RegistrationStage.create_from_dict_(RegistrationTemplate2t1, paths, config)

    def needed_files(self):
        return self.template2mprage,

    def parameters_for_comparing_past_runs(self):
        return self.PARAMETERS

    def make_commands_for_stage(self):
        commands = [

                    toolbox.ExternalCommand.get_command("flirt", f'-ref {self.atlas_template}', f'-in {self.mprage}',
                                                        f'-omat {self.mprage2template}', output_files=(self.mprage2template,),
                                                        input_files=(self.atlas_template, self.mprage)),
                    toolbox.ExternalCommand.get_command("fnirt", In=self.mprage, aff=self.mprage2template,
                                                        ref=self.atlas_template, cout=self.mprage2template,
                                                        config="/state/partition1/home/ronniek/ronniek/fnirtcnf/T1_2_MNI152_2mm", output_files=(self.mprage2template,),
                                                        input_files=(self.mprage, self.mprage2template,
                                                                     self.atlas_template)),
                    toolbox.ExternalCommand.get_command('invwarp', ref=self.mprage, out=self.template2mprage,
                                                        warp=self.mprage2template, output_files=(self.template2mprage,),
                                                        input_files=(self.mprage, self.mprage2template))
                   ]
        return commands


class RegistrationAtlas(RegistrationStage):
    PARAMETERS = RegistrationTemplate2t1.PARAMETERS + ['atlas_template', 'minvol']

    @staticmethod
    def create_from_dict(paths, config):
        return RegistrationStage.create_from_dict_(RegistrationAtlas, paths, config)

    def needed_files(self):
        return self.sub_atlas,

    def parameters_for_comparing_past_runs(self):
        return self.PARAMETERS

    def make_commands_for_stage(self):
        commands = [
                    toolbox.ExternalCommand.get_command("applywarp", ref=self.mprage, In=self.atlas, out=self.sub_atlas,
                                                        warp=self.template2mprage, interp="nn",
                                                        input_files=(self.mprage, self.atlas, self.template2mprage),
                                                        output_files=(self.sub_atlas,)),
                    toolbox.ExternalCommand.get_command("flirt", f"-applyxfm", f'-ref {self.brain}',
                                                        f'-in {self.sub_atlas}', f'-init {self.mprage2diff}',
                                                        f'-interp nearestneighbour', f'-out {self.sub_atlas}',
                                                        input_files=(self.sub_atlas, self.mprage2diff, self.brain,
                                                                     self.mprage2diff), output_files=(self.sub_atlas,))
                    ]
        return commands
