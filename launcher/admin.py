from django.contrib import admin

from .models import Submission


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    # Make all fields readonly
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['submitted', 'user', 'jobs', 'created']
        return []
