
#!/bin/bash
#$ -cwd
#$ -e qstOut/$JOB_NAME.ERR
#$ -o qstOut/$JOB_NAME.OUT


# Creating a file:
# touch /path/to/file

source /state/partition1/home/ronniek/.bashrc
cd /state/partition1/home/ronniek/ronniek/TAU_comissural_cortical_conections/
source venv/bin/activate
cd /state/partition1/home/ronniek/ronniek/ComisCortical/
python $1 $JOB_NAME $2
# TODO: create done files