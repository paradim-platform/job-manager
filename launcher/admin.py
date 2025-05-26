from django.contrib import admin

from .models import Submission, AggregationSubmission


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    # Make all fields readonly
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['submitted', 'user', 'jobs', 'created']
        return []


@admin.register(AggregationSubmission)
class AggregationSubmission(admin.ModelAdmin):
    # Make all fields readonly
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['state', 'filetype', 'user', 'runnable', 'album_id', 'created']
        return []
