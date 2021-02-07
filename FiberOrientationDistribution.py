from ComisCorticalCode import toolbox, stage
import os


class FiberOrientationDistribution(stage.Stage):
    def __init__(self, data, response, temp, mask, nthreads, fod, bv):
        self.commands = []
        self.data = data
        self.response = response
        self.responses = [os.path.join(temp, "gm_res.txt"), os.path.join(temp, "csf_res.txt")]
        self.fod = fod
        self.fods = [os.path.join(temp, "gm_fod.txt"), os.path.join(temp, "csf_fod.txt")]
        self.mask = mask
        self.nthreads = nthreads
        self.bv = bv

    @staticmethod
    def create_from_dict(paths, config):
        data = paths['data']
        response = paths['res']
        temp = paths['temp']
        mask = paths['mask']
        nthreads = config.NTHREADS
        fod = paths['fod']
        bv = [paths['bvecs'], paths['bvals']]
        return FiberOrientationDistribution(data, response, temp, mask, nthreads, fod, bv)

    def needed_files(self):
        return self.fod,

    def parameters_for_comparing_past_runs(self):
        return ['MINVOL']

    def make_commands_for_stage(self):
        # TODO: ask barak about the lists
        commands = [
                    toolbox.ExternalCommand.get_command("dwi2response", "dhollander", self.data, self.response,
                                                        " ".join(self.responses), '-force', mask=self.mask,
                                                        nthreads=self.nthreads, fslgrad=" ".join(self.bv),
                                                        input_files=(self.data, self.mask, self.bv[0], self.bv[1]),
                                                        output_files=tuple([self.response] +
                                                                           [f for f in self.responses])),
                    toolbox.ExternalCommand.get_command("dwi2fod msmt_csd", self.data, self.response, self.fod,
                                                        " ".join(sum(zip(self.responses, self.fods), ())), "-force",
                                                        fslgrad=" ".join(self.bv), nthreads=self.nthreads,
                                                        mask=self.mask, input_files=(self.data, self.response,
                                                                                     self.bv[0], self.bv[1], self.mask),
                                                        output_files=self.fod)
                   ]
        return commands
