import ComisCorticalCode as CC
import sys


def generate_stages_to_run():
    stages = [CC.Eddy.Eddy, CC.Registrations.Registrations, CC.Segmentation.Segmentation,
              CC.Generate_tracts.Generate_tracts, CC.Siftt_to_atlas.Siftt_to_atlas]
    return stages


def run_for_sub(subject_path, run_name):
    paths = CC.toolbox.get_paths(subject_path, run_name)
    for stage in generate_stages_to_run():
        s = stage.create_from_dict(paths)
        s.run()
        CC.toolbox.clear_dir(paths['temp'])


if __name__ == '__main__':
    sub_path = sys.argv[1]
    run = sys.argv[2]
    run_for_sub(sub_path, run)
