from django.db import models
from django.utils.translation import gettext_lazy as _


from manager.models.app import Modality, Runnable


class Job(models.Model):
    class State(models.TextChoices):
        APP_ERROR = 'APP_ERROR', _('The application encountered an unexpected error')
        CANCELLED = 'CANCELLED', _('The job was cancelled.')
        TECHNICAL_ERROR = 'TECHNICAL_ERROR', _('Error due to the platform, please contact PARADIM maintainers.')
        FINISHED = 'FINISHED', _('Successful')
        RUNNING = 'RUNNING', _('Running')
        SUBMITTED_TO_SLURM = 'SUBMITTED_TO_SLURM', _('Submitted to Slurm')
        SUBMITTED_TO_QUEUE = 'SUBMITTED_TO_QUEUE', _('Submitted to Queue')

    study_instance_uid = models.CharField(max_length=256)
    series_instance_uid = models.CharField(max_length=256)
    slurm_id = models.IntegerField(unique=True, blank=True, null=True)
    runnable = models.ForeignKey(Runnable, on_delete=models.DO_NOTHING)
    state = models.CharField(max_length=64, choices=State.choices)
    last_change = models.DateTimeField(auto_now=True)
    # This is present when the job requests results in a specified album.
    kheops_album_id = models.CharField(max_length=256, blank=True, null=True)
    logs = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ['series_instance_uid', 'runnable']

    def __str__(self):
        return f'Job({self.slurm_id}, {self.state}, {self.runnable.app.name}:{self.runnable.version})'

    @property
    def job_filename(self) -> str:
        return f'{self.runnable.app.name}-{self.runnable.version}-{self.series_instance_uid}.job'

    @property
    def zip_filename(self) -> str:
        return f'{self.runnable.app.name}-{self.runnable.version}-{self.series_instance_uid}.zip'


class GeneratedSeries(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    modality = models.ForeignKey(Modality, blank=True, null=True, on_delete=models.DO_NOTHING)
    series_instance_uid = models.CharField(max_length=256)
    is_technical_sr = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.modality:
            return f'GeneratedSeries({self.modality.abbreviation}, {self.series_instance_uid}, {self.job})'

        return f'GeneratedSeries(Unknown, {self.series_instance_uid}, {self.job})'
