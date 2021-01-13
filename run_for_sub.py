import ComisCorticalCode as CC
import sys
import os


def generate_stages_to_run():
    stages = [CC.Eddy.Eddy, CC.Registrations.Registrations, CC.Segmentation.Segmentation,
              CC.Generate_tracts.Generate_tracts, CC.Siftt_to_atlas.Sift_to_atlas]
    return stages


def run_for_sub(subject_path, run_name, out_path):
    config = CC.CONFIG.CONFIG.from_json(os.path.join(out_path, 'config_files', run_name))
    paths = CC.toolbox.get_paths(subject_path, run_name)
    for stage in generate_stages_to_run():
        s = stage.create_from_dict(paths, config)
        s.run()
        CC.toolbox.clear_dir(paths['temp'])


if __name__ == '__main__':
    run_for_sub(*sys.argv[1:])
