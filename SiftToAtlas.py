from ComisCorticalCode import toolbox, stage
import os
import nibabel as nb
import numpy as np
# TODO: change file name without killing it in git?


class SiftToAtlas(stage.Stage):
    def __init__(self, *, atlas, atlas_for_connectome, temp, nthreads, tracts, fod, sifted_atlas_tracts, segmentation,
                 ntracts):
        self.atlas = atlas
        self.atlas_for_connectome = atlas_for_connectome
        self.connectome_atlas = os.path.join(temp, 'conncetome_atlas.nii.gz')
        self.temp = temp
        self.nthreads = nthreads
        self.connectome_out = os.path.join(self.temp, 'out')
        self.tracts = tracts
        self.atlas_tracts = os.path.join(temp, 'atlas_tracts.tck')
        self.fod = fod
        self.sifted_atlas_tracts = sifted_atlas_tracts
        self.segmentation = segmentation
        self.ntracts = ntracts

    @staticmethod
    def create_from_dict(paths, config):
        atlas = paths['atlas']
        atlas_for_connectome = config.atlas_for_connectome
        temp = paths['temp']
        nthreads = config.nthreads
        tracts = paths["tracts"]
        fod = paths['fod']
        sifted_atlas_tracts = paths["sifted_atlas_tracts"]
        segmentation = paths["5tt"]
        ntracts = config.ntracts
        return SiftToAtlas(atlas=atlas,
                           atlas_for_connectome=atlas_for_connectome,
                           temp=temp,
                           nthreads=nthreads,
                           tracts=tracts,
                           fod=fod,
                           sifted_atlas_tracts=sifted_atlas_tracts,
                           segmentation=segmentation,
                           ntracts=ntracts)

    def parameters_for_comparing_past_runs(self):
        return ['MINVOL', 'NTRACTS', 'LINSCALE', 'STEPSCALE', 'ANGLE', 'ATLAS']

    def needed_files(self):
        return self.atlas_tracts,

    def make_commands_for_stage(self):
        commands = [
                    toolbox.ExternalCommand.get_command("labelconvert", self.atlas, self.atlas_for_connectome,
                                                        self.atlas_for_connectome('.txt', '_converted.txt'),
                                                        self.connectome_atlas, "force", nthreads=self.nthreads,
                                                        input_files=(self.atlas, self.atlas_for_connectome),
                                                        output_files=(self.atlas_for_connectome('.txt',
                                                                                                '_converted.txt'),
                                                        self.connectome_atlas)),
                    toolbox.ExternalCommand.get_command("tck2connectome", self.connectome_atlas,
                                                        os.path.join(self.temp, 'connectome'), "-force",
                                                        nthreads=self.nthreads, assignment_radial_search=2,
                                                        out_assignments=self.connectome_out,
                                                        input_files=(self.connectome_atlas,),
                                                        output_files=(self.connectome_out,)),
                    toolbox.ExternalCommand.get_command("connectome2tck", self.tracts, self.connectome_out,
                                                        self.atlas_tracts, "-exclusive", "-keep_self", "-force",
                                                        nthreads=self.nthreads, nodes=self.list_of_nodes(),
                                                        files="single", input_files=(self.tracts, self.connectome_out),
                                                        output_files=(self.atlas_tracts,)),
                    toolbox.ExternalCommand.get_command("tcksift", self.atlas_tracts, self.fod,
                                                        self.sifted_atlas_tracts, "-force", "-fd_scale_gm",
                                                        act=self.segmentation, nthreads=self.nthreads,
                                                        term_number=self.ntracts * 0.1,
                                                        input_files=(self.atlas_tracts, self.fod, self.segmentation),
                                                        output_files=(self.sifted_atlas_tracts,))
                    ]
        return commands

    def list_of_nodes(self):
        parc = nb.load(self.atlas).get_data()
        return ",".join([str(i) for i in range(1, len(np.unique(parc)))])
