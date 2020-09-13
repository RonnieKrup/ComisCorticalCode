from ComisCorticalCode import toolbox, CSV
import shutil
import ComisCorticalCode as CC


def generate_stages_to_run():
    stages = [CC.Eddy.Eddy, CC.Registrations.Registrations, CC.Segmentation.Segmentation,
              CC.Generate_tracts.Generate_tracts, CC.Siftt_to_atlas.Siftt_to_atlas]
    return stages


def run(sub_dirs):
    #TO DO: take subject loop out of the function for per-job

    run_name = CSV.get_run_name()
    shutil.copyfile('./CONFIG.py', f'./config_files/{run_name}.py')
    CSV.update_new_runs(run_name)
    for subject in sub_dirs:
        paths = toolbox.get_paths(subject, run_name)
        for stage in generate_stages_to_run():
            s = stage.create_from_dict(paths)
            s.run()
            toolbox.clear_dir(paths['temp'])
    CSV.update_old_runs()
