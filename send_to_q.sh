
#!/bin/bash
#$ -cwd
#$ -e qstOut/JOB_NAME.ERR
#$ -o qstOut/JOB_NAME.OUT


# Creating a file:
# touch /path/to/file

source /state/partition1/home/ronniek/.bashrc
cd /state/partition1/home/ronniek/ronniek/TAU_comissural_cortical_conections/ || { echo "couldn't activate venv"; exit 1; }
source venv/bin/activate
cd /state/partition1/home/ronniek/ronniek/ComisCortical/ || { echo "couldn't activate venv"; exit 1; }
touch OUT_PATH/RUN_NAME/JOB_NAME.STARTED
python SCRIPT_TO_RUN SUBJECT_PATH RUN_NAME OUT_PATH
mv OUT_PATH/RUN_NAME/JOB_NAME.STARTED OUT_PATH/RUN_NAME/JOB_NAME.DONE