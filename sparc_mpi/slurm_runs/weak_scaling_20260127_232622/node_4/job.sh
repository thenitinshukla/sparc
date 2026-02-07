#!/bin/bash -l
#SBATCH -A cin_staff
#SBATCH --partition=dcgp_usr_prod
##SBATCH --qos=dcgp_qos_bprod
#SBATCH --job-name="th_4"
#SBATCH --time=01:00:00
#SBATCH -D .
#SBATCH --output=job.out.%j
#SBATCH --error=job.err.%j
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=112
#SBATCH --contiguous
#SBATCH --exclusive

module load openmpi/4.1.6--gcc--12.2.0-cuda-12.2

dat1=`date +"%Y-%m-%d %H:%M:%S"`

echo " " > "$SLURM_JOB_ID.dat"
echo SLURM_JOB_CPUS_PER_NODE=$SLURM_JOB_CPUS_PER_NODE >> "$SLURM_JOB_ID.dat"
echo SLURM_CPUS_PER_TASK=$SLURM_CPUS_PER_TASK >> "$SLURM_JOB_ID.dat"
echo SLURM_CPU_BIND=$SLURM_CPU_BIND >> "$SLURM_JOB_ID.dat"
echo SLURM_DISTRIBUTION=$SLURM_DISTRIBUTION >> "$SLURM_JOB_ID.dat"
echo SLURM_JOB_NODELIST=$SLURM_JOB_NODELIST >> "$SLURM_JOB_ID.dat"
echo SLURM_TASKS_PER_NODE=$SLURM_TASKS_PER_NODE >> "$SLURM_JOB_ID.dat"
echo SLURM_STEP_NODELIST=$SLURM_STEP_NODELIST >> "$SLURM_JOB_ID.dat"
echo SLURM_STEP_NUM_NODES=$SLURM_STEP_NUM_NODES >> "$SLURM_JOB_ID.dat"
echo SLURM_STEP_NUM_TASKS=$SLURM_STEP_NUM_TASKS >> "$SLURM_JOB_ID.dat"
echo SLURM_STEP_TASKS_PER_NODE=$SLURM_STEP_TASKS_PER_NODE >> "$SLURM_JOB_ID.dat"
echo SLURM_JOB_NUM_NODES=$SLURM_JOB_NUM_NODES >> "$SLURM_JOB_ID.dat"
echo SLURM_NTASKS=$SLURM_NTASKS >> "$SLURM_JOB_ID.dat"
echo SLURM_NPROCS=$SLURM_NPROCS >> "$SLURM_JOB_ID.dat"
echo SLURM_CPUS_ON_NODE=$SLURM_CPUS_ON_NODE >> "$SLURM_JOB_ID.dat"
echo SLURM_NODEID=$SLURM_NODEID >> "$SLURM_JOB_ID.dat"
echo SLURMD_NODENAME=$SLURMD_NODENAME >> "$SLURM_JOB_ID.dat"

EXECUTABLE=/leonardo_scratch/large/userinternal/nshukla1/PICKTH/sparc_mpi

srun --cpu-bind=cores $EXECUTABLE/sparc_mpi input_file.txt -n

dat2=`date +"%Y-%m-%d %H:%M:%S"`

echo "Start: $dat1"
echo "Finish: $dat2"

exit
