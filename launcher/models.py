from django.contrib.auth.models import User
from django.db import models

from manager.models import Job


class Submission(models.Model):
    submitted = models.BooleanField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    jobs = models.ManyToManyField(Job)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Submission-{self.user.email}-{self.created.strftime('%Y-%m-%d')}"
