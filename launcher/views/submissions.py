from django.db.models import Prefetch
from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse
from rest_framework.reverse import reverse_lazy

from launcher.models import Submission
from manager.models import Job


def submissions_view(request: HttpRequest) -> HttpResponse:
    submissions = Submission.objects.filter(user=request.user)

    return TemplateResponse(request, 'jobs/submitted_jobs.html', {'submissions': submissions.order_by('-created')})


def submission_view(request: HttpRequest, submission_id: str) -> HttpResponse:
    try:
        submission = (
            Submission.objects
            .prefetch_related(
                Prefetch(
                    'jobs',
                    queryset=Job.objects.select_related('runnable', 'runnable__app').defer('logs')
                )
            )
            .get(user=request.user, id=submission_id)
        )
    except Submission.DoesNotExist:
        return HttpResponse(f'{submission_id} does not exist anymore')

    if not submission.submitted:
        return HttpResponse(f"""
                <div hx-get="{reverse_lazy('submissions-detail', kwargs={'submission_id': submission_id})}" 
                     hx-trigger="every 5s"
                     hx-swap="outerHTML">
                  <p>{str(submission)}</p>
                  <div id="spinner" class="spinner-border ml-2" role="status">
                    <span class="visually-hidden">Loading...</span>
                  </div>
                </div>
                """)

    job_statues_html = ''
    nbr_of_success = 0
    nbr_of_pending = 0
    nbr_of_failure = 0
    for job in submission.jobs.all():
        if job.state in [Job.State.APP_ERROR, Job.State.TECHNICAL_ERROR]:
            status_html = 'text-bg-danger'
            status_class = 'submission-failure'
            nbr_of_failure += 1
        elif job.state in [Job.State.FINISHED]:
            status_html = 'text-bg-success'
            status_class = 'submission-success'
            nbr_of_success += 1
        else:
            status_html = 'text-bg-warning'
            status_class = 'submission-pending'
            nbr_of_pending += 1

        # !html
        job_statues_html += f"""
            <div class="card my-2 {status_html} submission-item {status_class}">
                <div class="card-body" style="cursor: pointer;" onclick="location.href='{reverse_lazy('jobs-details', kwargs={'job_id': job.id})}';">
                    {job.state} - {job.runnable.app.name}:{job.runnable.version} {job.series_instance_uid}
                </div>
            </div>
        """

    return HttpResponse(f"""
            <div>
              <button class="btn" type="button" data-bs-toggle="collapse" data-bs-target="#{submission_id}_collapse">
                  <p>{str(submission)}</p>
                  <p>Success: {nbr_of_success}, Pending/running: {nbr_of_pending}, Failure: {nbr_of_failure} </p>
              </button>
              <div class="collapse" id="{submission_id}_collapse">
                <div class="col">
                    {job_statues_html}   
                </div>
              </div>               
            </div>
            """)
