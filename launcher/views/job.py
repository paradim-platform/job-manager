from http import HTTPStatus

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path
from django.utils.translation import gettext_lazy as _
from django.contrib import messages

from manager.models import Job
from manager.services.jobs import rerun_job


def job_detail_view(request: HttpRequest, job_id: str):
    job = Job.objects.get(id=job_id)

    # Validate if user can see the job detail.
    # User should have this job in one of its submission.
    if not job.submission_set.filter(user=request.user).exists():
        return HttpResponse(_('You are not authorized to see this Job detail'), status=HTTPStatus.FORBIDDEN)

    return TemplateResponse(request, 'jobs/job_detail.html', {'job': job})


def rerun_job_view(request: HttpRequest, job_id: str):
    if request.method != 'POST':
        return HttpResponse(_('Method not allowed'), status=HTTPStatus.METHOD_NOT_ALLOWED)

    job = Job.objects.get(id=job_id)

    # Validate if user can rerun the job
    if not job.submission_set.filter(user=request.user).exists():
        return HttpResponse(_('You are not authorized to rerun this job'), status=HTTPStatus.FORBIDDEN)

    rerun_job(job)
    messages.success(request, _('Job has been scheduled for rerun'))

    return redirect('jobs-details', job_id=job_id)
