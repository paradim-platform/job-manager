import textwrap

from manager.models import Job
from .compute_sizes import find_compute_config
from .config import DICOM_WEB_URL, JOB_MANAGER_URL


def make_slurm_file(job: Job, dist_dirname: str, paradim_token: str, additional_info: str = None) -> str:
    if additional_info is None:
        additional_info = ''

    compute_config = find_compute_config(job.runnable.size, job.runnable.with_gpu)

    return textwrap.dedent(
        f"""
        #!/bin/bash
        # ---------------------------------------------------------------------
        # SLURM script for job submission on clusters (valeria).
        # Note: the script may not be compatible with compute canada due to the need of internet
        # ---------------------------------------------------------------------
        #SBATCH --job-name=job-{job.runnable.app.name}:{job.runnable.version}
        #SBATCH --cpus-per-task={compute_config.cpu}
        #SBATCH --mem={compute_config.memory}
        #SBATCH --time={compute_config.time}
        #SBATCH --partition={compute_config.partition}
        #SBATCH --output={job.runnable.app.name}:{job.runnable.version}-%j.out
        {'#SBATCH --gpus-per-node=1' if job.runnable.with_gpu else ''}
        
        # Chargement des modules
        module load apptainer/1.1.8
        module load python/3.11
        
        # Fix for Valeria compatibility
        export APPTAINER_BIND="/project,/scratch"
        
        {'module load cuda' if job.runnable.with_gpu else ''}
        
       
        source venv/bin/activate
        
        paradim run --img=$PARADIM_IMAGES_PATH/{job.runnable.app.name}_{job.runnable.version}.sif --data={dist_dirname}/{job.zip_filename} \\
                    --series-instance-uid={job.series_instance_uid} --token={paradim_token} \\
                    --job-management=https://{JOB_MANAGER_URL} --dicom-web={DICOM_WEB_URL} \\
                    --with-gpu={job.runnable.with_gpu} --additional-info="{additional_info}" \\
                    --scheduler=slurm
                
        rm -f {dist_dirname}/{job.zip_filename}
        """
    ).strip('\n')
