from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from manager.models import Job, Runnable


class Submission(models.Model):
    submitted = models.BooleanField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    jobs = models.ManyToManyField(Job)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Submission-{self.user.email}-{self.created.strftime('%Y-%m-%d')}"


class AggregationSubmission(models.Model):
    class FileType(models.TextChoices):
        CSV = 'csv', 'CSV'
        JSON = 'json', 'JSON'

    class State(models.TextChoices):
        COMPLETED = 'C', _('Completed')
        ERROR = 'E', _('Error')
        RUNNING = 'R', _('Running')
        SUBMITTED = 'S', _('Submitted')

    filetype = models.CharField(max_length=4, choices=FileType.choices)
    state = models.CharField(max_length=64, choices=State.choices)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    runnable = models.ForeignKey(Runnable, on_delete=models.DO_NOTHING)
    album_id = models.CharField(max_length=256, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)

    result = models.TextField(default='')

    def __str__(self):
        return f"{self.runnable.app.name}:{self.runnable.version}-{self.album_id}-{self.user.email}-{self.created.strftime('%Y-%m-%d')}-{self.get_state_display()}"
