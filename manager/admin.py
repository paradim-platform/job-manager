from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import App, GeneratedSeries, Job, Level, Modality, Runnable, Size
from .services.jobs import rerun_job


@admin.register(App)
class AppAdmin(admin.ModelAdmin):
    pass


@admin.register(Modality)
class ModalityAdmin(admin.ModelAdmin):
    pass


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    pass


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    pass


@admin.register(Runnable)
class RunnableAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Runnable._meta.fields] + ['automatic_run']
    readonly_fields = ['automatic_run']

    def automatic_run(self, obj: Runnable):
        return obj.app.automatic_run


@admin.action(description='Rerun selected jobs')
def rerun_jobs(_: admin.ModelAdmin, __: HttpRequest, queryset: QuerySet):
    for job in queryset:
        rerun_job(job)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    actions = [rerun_jobs]

    list_display = ['slurm_id', 'state', 'app', 'version', 'study_instance_uid', 'series_instance_uid', 'last_change']
    list_filter = ['state', 'runnable__app__name']

    search_help_text = 'Enter a study/series uid, slurm id, app name or version'
    search_fields = ['study_instance_uid', 'series_instance_uid', 'slurm_id', 'runnable__app__name',
                     'runnable__version']

    ordering = ['-last_change']
    readonly_fields = ['slurm_id', 'state', 'app', 'study_instance_uid', 'series_instance_uid', 'last_change',
                       'generated_series_list']

    def app(self, job: Job):
        return job.runnable.app.name

    def version(self, job: Job):
        return job.runnable.version

    def generated_series_list(self, job: Job):
        html = []

        for generated_series in GeneratedSeries.objects.filter(job=job):
            if generated_series.modality:
                html.append(
                    f'<span>{generated_series.modality.abbreviation}-{generated_series.series_instance_uid}</span>')
            else:
                html.append(f'<span>Unknown-{generated_series.series_instance_uid}</span>')

        return mark_safe('[' + ', '.join(html) + ']')

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:  # Means in editing mode, else is add mode
            return self.readonly_fields

        return []


@admin.register(GeneratedSeries)
class GeneratedSeries(admin.ModelAdmin):
    list_display = ['series_instance_uid', 'created', 'job', 'is_technical_sr']

    search_help_text = 'Enter a series uid or a job id'
    search_fields = ['series_instance_uid', 'job__slurm_id', 'job__runnable__app__name']

    readonly_fields = ['series_instance_uid', 'created', 'job', 'is_technical_sr']

    def job(self, generated_series: GeneratedSeries):
        change_url = reverse('admin:job_manager_job_change', args=(generated_series.job.id,))

        return mark_safe(
            f'<a href="{change_url}">'
            f'{generated_series.job.slurm_id}, '
            f'{generated_series.job.runnable.app.name}:{generated_series.job.runnable.version}'
            f'</a>'
        )

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:  # Means in editing mode, else is added mode
            return self.readonly_fields

        return []
