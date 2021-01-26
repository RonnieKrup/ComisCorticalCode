from ComisCorticalCode import Eddy, Registrations, Segmentation, Generate_tracts, Siftt_to_atlas, CONFIG, toolbox
import sys
import os


def generate_stages_to_run():
    stages = [Eddy.Eddy, Registrations.RegistrationT12diff, Registrations.RegistrationTemplate2t1,
              Registrations.RegistrationAtlas, Segmentation.Segmentation,
              Generate_tracts.Generate_tracts, Siftt_to_atlas.Sift_to_atlas]
    return stages


def run_for_sub(subject_path, run_name, out_path):
    config = CONFIG.CONFIG.from_json(os.path.join(out_path, 'config_files', run_name))
    paths = toolbox.get_paths(subject_path, run_name)
    for stage in generate_stages_to_run():
        s = stage.create_from_dict(paths, config)
        s.run()
        toolbox.clear_dir(paths['temp'])


def test_run():
    toolbox.DRY_RUN = True  # Don't actually run anything or touch files
    config = CONFIG.CONFIG.from_json("/state/partition1/home/ronniek/ronniek/tb4e_test/test.json")
    print(config)


if __name__ == '__main__':
    #run_for_sub(*sys.argv[1:])
    test_run()
