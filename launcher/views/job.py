from http import HTTPStatus

from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _

from manager.models import Job


def job_detail_view(request: HttpRequest, job_id: str):
    job = Job.objects.get(id=job_id)

    # Validate if user can see the job detail.
    # User should have this job in one of its submission.
    if not job.submission_set.filter(user=request.user).exists():
        return HttpResponse(_('You are not authorized to see this Job detail'), status=HTTPStatus.FORBIDDEN)

    return TemplateResponse(request, 'jobs/job_detail.html', {'job': job})
