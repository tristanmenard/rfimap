import pathlib
from pandas import read_csv
from datetime import timedelta
from argparse import ArgumentParser

"""
Example usage: python job_template.py /scratch/group/user/projectname /project/group/user /project/group/user/projectname/elevation.pickle /project/group/user/projectname/txdb.csv
"""
parser = ArgumentParser(description='Template bash script for a job on a given node.')
parser.add_argument('work_dir', type=str, help='absolute path to working directory used for project')
parser.add_argument('rasp_dir', type=str, help='absolute path to rasp parent directory')
parser.add_argument('elevation_fname', type=str, help='absolute path to pickled elevation data file used for project')
parser.add_argument('txdb_fname', type=str, help='absolute path to CSV transmitter database used for project')
# parser.add_argument('--total_txs', type=int, help='total number of transmitters')
parser.add_argument('--txs_per_node', type=int, default=80, help='amount of single transmitter power maps computed per node (default=80, recommended: 40-80)')
parser.add_argument('--job_name', type=str, help='job name as it appears on Niagara queue and in log files (default: name of final directory in work_dir)')
parser.add_argument('--max_time', type=float, default=3, help='maximum time in hours allowed for the job to complete on a given node (default: 3)')
parser.add_argument('--python_env_bin', type=str, default='~/.virtualenvs/myenv/bin', help='bin directory for custom python environment (default: ~/.virtualenvs/myenv/bin)')
args = parser.parse_args()

work_dir = pathlib.Path(args.work_dir)
rasp_dir = pathlib.Path(args.rasp_dir)
elevation_fname = pathlib.Path(args.elevation_fname)
txdb_fname = pathlib.Path(args.txdb_fname)
python_env_bin = pathlib.Path(args.python_env_bin)
python_env_activate = python_env_bin.joinpath('activate')

if args.job_name:
	job_name = args.job_name
else:
	job_name = work_dir.name

max_time = str(timedelta(hours=args.max_time))

total_txs = len(read_csv(txdb_fname))

total_nodes = (total_txs-1) // args.txs_per_node + 1
print(f'Writing job scripts for {total_nodes} nodes...')

for node_num in range(total_nodes):
	bash_fname = work_dir.joinpath(f'node{node_num}/{args.project_name}_node{node_num}_job.sh')
	bash_fname.parent.mkdir(parents=True, exist_ok=True)

	txfirst = node_num*args.txs_per_node
	txlast = (node_num+1)*args.txs_per_node - 1
	if node_num == total_nodes - 1:
		txlast = total_txs - 1

	template = f"""#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node={args.txs_per_node}
#SBATCH --time={max_time}
#SBATCH --job-name {job_name}_{node_num}
#SBATCH --mail-type=FAIL

# Go to job working directory
cd {work_dir}

# Turn off implicit threading in Python
export OMP_NUM_THREADS=1

# Load gnu-parallel
module load gnu-parallel

# Activate custom python 3 environment
source {python_env_activate}

# Add rasp to PYTHONPATH
export PYTHONPATH="$PYTHONPATH:{rasp_dir}"

parallel --joblog slurm-$SLURM_JOBID.log -j $SLURM_TASKS_PER_NODE "python singleTxmap.py' {{}} {node_num} {elevation_fname} {txdb_fname}" ::: {{{txfirst}..{txlast}}}
"""

	with open(bash_fname, 'w') as f:
		f.write(template)
