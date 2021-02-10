from ComisCorticalCode import Eddy, Resample, Registrations, Segmentation, FiberOrientationDistribution, GenerateTracts, SiftToAtlas, Config, toolbox
import sys
import os


def generate_stages_to_run(config):
    stages = [Eddy.Eddy, Resample.Resample, Registrations.RegistrationT12diff, Registrations.RegistrationTemplate2t1,
              Registrations.RegistrationAtlas, Segmentation.Segmentation, Segmentation.SegmentRegistration,
              FiberOrientationDistribution.FiberOrientationDistribution, GenerateTracts.GenerateTracts,
              SiftToAtlas.SiftToAtlas]
    if not config.minvol:
        stages.remove(Resample.Resample)
    return stages


def run_for_sub(subject_path, run_name, out_path):
    config = Config.Config.from_json(os.path.join(out_path, 'config_files', f'{run_name}.json'))
    paths = toolbox.get_paths(subject_path, run_name)
    for stage in generate_stages_to_run(config):
        s = stage.create_from_dict(paths, config)
        s.run_stage(config.run_list)
        toolbox.clear_dir(paths['temp'])


if __name__ == '__main__':
    if toolbox.DRY_RUN:
        run_for_sub('/mnt/e/Ronniek/ComisCorticalCode/test_data/sub', 'test',
                    '/mnt/e/Ronniek/ComisCorticalCode/test_data/out')
    run_for_sub(*sys.argv[1:])
