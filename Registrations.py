from ComisCorticalCode import toolbox, stage
import os


class RegistrationStage(stage.Stage):
    def __init__(self, *, mprage, temp, brain, mprage2diff, atlas_template, template2mprage, atlas, subject_atlas):
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
    def create_from_dict_(cls, paths, config):
        # cls is the class to create
        mprage = paths['mprage']
        temp = paths["temp"]
        brain = paths.brain
        mprage2diff = paths["mprage2diff"]
        atlas_template = config.atlas_template
        template2mprage = paths["template2mprage"]
        atlas = config.atlas
        subject_atlas = paths["atlas"]
        return cls(
            mprage=mprage,
            temp=temp,
            brain=brain,
            mprage2diff=mprage2diff,
            atlas_template=atlas_template,
            template2mprage=template2mprage,
            atlas=atlas,
            subject_atlas=subject_atlas)


class RegistrationT12diff(RegistrationStage):
    PARAMETERS = ['MINVOL']

    @staticmethod
    def create_from_dict(paths, config):
        return RegistrationStage.create_from_dict_(RegistrationT12diff, paths, config)

    def needed_files(self):
        return self.mprage2diff,

    def parameters_for_comparing_past_runs(self):
        return self.PARAMETERS

    def make_commands_for_stage(self):
        commands = [
                    toolbox.ExternalCommand.get_command('bet', self.mprage, self.mprage_brain, '-m', f=0.2, g=0.2,
                                                        input_files=(self.mprage,),
                                                        output_files=(self.mprage_brain,)),
                    toolbox.ExternalCommand.get_command('flirt', In=self.brain, ref=self.mprage_brain,
                                                        omat=self.dif2mprage, bins=256, cost="normmi",
                                                        searchrx="-90 90", searchry="-90 90",
                                                        searchrz="-90 90", dof=12, output_files=(self.dif2mprage,),
                                                        input_files=(self.brain, self.mprage_brain)),
                    toolbox.ExternalCommand.get_command("convert_xfm", self.dif2mprage, "-inverse",
                                                        omat=self.mprage2diff, input_files=(self.dif2mprage,),
                                                        output_files=(self.mprage2diff,))
                    ]
        return commands


class RegistrationTemplate2t1(RegistrationStage):
    PARAMETERS = ['ATLAS_TEMPLATE'] + RegistrationT12diff.PARAMETERS

    @staticmethod
    def create_from_dict(paths, config):
        return RegistrationStage.create_from_dict_(RegistrationTemplate2t1, paths, config)

    def needed_files(self):
        return self.template2mprage,

    def parameters_for_comparing_past_runs(self):
        return self.PARAMETERS

    def make_commands_for_stage(self):
        commands = [

                    toolbox.ExternalCommand.get_command("flirt", ref=self.atlas_template, In=self.mprage,
                                                        omat=self.mprage2template, output_files=(self.mprage2template,),
                                                        input_files=(self.atlas_template, self.mprage)),
                    toolbox.ExternalCommand.get_command("fnirt", In=self.mprage, aff=self.mprage2template,
                                                        ref=self.atlas_template, cout=self.mprage2template,
                                                        config="T1_2_MNI152_2mm", output_files=(self.mprage2template,),
                                                        input_files=(self.mprage, self.mprage2template,
                                                                     self.atlas_template)),
                    toolbox.ExternalCommand.get_command('invwarp', ref=self.mprage, out=self.template2mprage,
                                                        warp=self.mprage2template, output_files=(self.template2mprage,),
                                                        input_files=(self.mprage, self.mprage2template))
                   ]
        return commands


class RegistrationAtlas(RegistrationStage):
    PARAMETERS = RegistrationTemplate2t1.PARAMETERS + ['ATLAS_TEMPLATE', 'MINVOL']

    @staticmethod
    def create_from_dict(paths, config):
        return RegistrationStage.create_from_dict_(RegistrationAtlas, paths, config)

    def needed_files(self):
        return self.atlas,

    def parameters_for_comparing_past_runs(self):
        return self.PARAMETERS

    def make_commands_for_stage(self):
        commands = [
                    toolbox.ExternalCommand.get_command("applywarp", ref=self.mprage, In=self.atlas, out=self.atlas,
                                                        warp=self.template2mprage, interp="nn",
                                                        input_files=(self.mprage, self.atlas, self.template2mprage),
                                                        output_files=(self.atlas,)),
                    toolbox.ExternalCommand.get_command("flirt", "applyxfm", ref=self.brain, In=self.atlas,
                                                        init=self.mprage2diff, interp="nearestneighbour",
                                                        out=self.atlas, input_files=(self.atlas, self.mprage2diff,
                                                                                     self.brain, self.mprage2diff),
                                                        output_files=(self.atlas,))
                    ]
        return commands
