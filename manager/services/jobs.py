from manager.models import Job
from manager.serializers import JobWithoutConstraintValidationSerializer


def rerun_job(job: Job):
    from executor.executor import setup_and_submit_slurm_job

    job_data = JobWithoutConstraintValidationSerializer(job).data
    setup_and_submit_slurm_job.apply_async(
        kwargs={'job_data': job_data},
        priority=5
    )

    # Update state
    job.state = Job.State.SUBMITTED_TO_QUEUE
    job.save()
