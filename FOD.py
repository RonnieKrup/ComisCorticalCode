from ComisCorticalCode import CONFIG, CSV, toolbox
import os

class FOD:
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
    def create_from_dict(paths):
        data = paths['data']
        response = paths['res']
        temp = paths['temp']
        mask = paths['mask']
        nthreads = CONFIG.NTHREADS
        fod = paths['fod']
        bv = [paths['bvecs'], paths['bvals']]
        return FOD(data, response, temp, mask, nthreads, fod, bv)

    def run(self):
        if not os.path.isfile(self.fod):
            past_run = CSV.find_past_runs(['MINVOL'])
            if past_run:
                needed_files = (self.fod,)
                toolbox.make_link(past_run, needed_files)
            else:
                self.make_fod()
        toolbox.run_commands(self.commands)

    def make_fod(self):
        self.commands.append(
            toolbox.get_command("dwi2response", ("dhollander", self.data, self.response, " ".join(self.responses),
                                                 '-force'), mask=self.mask, nthreads=self.nthreads,
                                fslgrad=" ".join(self.bv)))

        self.commands.append(toolbox.get_command("dwi2fod msmt_csd", (self.data, self.response, self.fod,
                                                                      " ".join(sum(zip(self.responses, self.fods), ())),
                                                                      "-force"), fslgrad=" ".join(self.bv),
                                                 nthreads=self.nthreads, mask=self.mask))
