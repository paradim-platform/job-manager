from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from . import models
from .models import Job


class RunnableSerializer(serializers.ModelSerializer):
    app = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()
    modality = serializers.SerializerMethodField()

    class Meta:
        model = models.Runnable
        fields = ['app', 'version', 'level', 'modality', 'size', 'with_gpu']

    def get_app(self, obj: models.Runnable) -> str:
        return obj.app.name

    def get_size(self, obj: models.Runnable) -> str:
        return obj.size.abbreviation

    def get_level(self, obj: models.Runnable) -> str:
        return obj.level.value

    def get_modality(self, obj: models.Runnable) -> str:
        return obj.modality.abbreviation


class RunnablesSerializer(serializers.Serializer):
    runnables = RunnableSerializer(many=True)


class AppInfoSerializer(serializers.Serializer):
    """This serializer contains the app info to find the correct runnable"""
    name = serializers.CharField()
    version = serializers.CharField()


class JobSerializer(serializers.ModelSerializer):
    app_info = AppInfoSerializer()
    generated_series_instance_uids = serializers.SerializerMethodField()

    class Meta:
        model = models.Job
        fields = ['slurm_id', 'state', 'series_instance_uid', 'study_instance_uid', 'app_info',
                  'generated_series_instance_uids', 'logs']

    def get_generated_series_instance_uids(self, job: models.Job) -> list[str]:
        """Retrieve the Generated series UID corresponding to the job."""
        return [i.series_instance_uid for i in models.GeneratedSeries.objects.filter(job=job)]

    def create(self, validated_data: dict) -> models.Job:
        # pop app_info since it is not part of models.Job
        app_info = validated_data.pop('app_info')
        runnable = _find_runnable(app_info['name'], app_info['version'])

        if self.Meta.model.objects.filter(runnable=runnable,
                                          series_instance_uid=validated_data['series_instance_uid']).exists():
            raise ValidationError(f'This Job already exists {validated_data}')

        return models.Job.objects.create(**validated_data, runnable=runnable)

    def to_representation(self, instance: models.Job):
        return {
            'slurm_id': instance.slurm_id,
            'state': instance.state,
            'series_instance_uid': instance.series_instance_uid,
            'study_instance_uid': instance.study_instance_uid,
            'app_info': {
                'name': instance.runnable.app.name,
                'version': instance.runnable.version
            },
            'generated_series_instance_uids': self.get_generated_series_instance_uids(instance)
        }


class GeneratedSeriesSerializer(serializers.ModelSerializer):
    source_series_instance_uid = serializers.CharField()
    app_info = AppInfoSerializer()

    class Meta:
        model = models.GeneratedSeries
        fields = ['series_instance_uid', 'modality', 'app_info', 'source_series_instance_uid']

    def create(self, validated_data: dict) -> models.Job:
        # Find the corresponding job before creating a GeneratedSeries
        app_info = validated_data.pop('app_info')
        runnable = _find_runnable(app_info['name'], app_info['version'])

        source_series_instance_uid = validated_data.pop('source_series_instance_uid')
        job = _find_job(runnable, source_series_instance_uid)

        return models.GeneratedSeries.objects.create(**validated_data, job=job)

    def to_representation(self, instance: models.GeneratedSeries):
        return {
            'series_instance_uid': instance.series_instance_uid,
            'job': {
                'source_series_instance_uid': instance.series_instance_uid,
                'app_info': {
                    'name': instance.job.runnable.app.name,
                    'version': instance.job.runnable.version,
                    'modality': instance.job.runnable.modality.abbreviation,
                },
            }
        }


def _find_runnable(app_name: str, app_version: str) -> models.Runnable:
    runnables = models.Runnable.objects.filter(app__name=app_name, version=app_version)

    if not runnables.exists():
        error_detail = {'app_info': [f'Runnable not find for name={app_name}, version={app_version}']}
        raise ValidationError(error_detail)

    return runnables.first()


def _find_job(runnable: models.Runnable, series_instance_uid: str) -> models.Job:
    jobs = models.Job.objects.filter(runnable=runnable, series_instance_uid=series_instance_uid)

    if not jobs.exists():
        error_detail = {'app_info-source_series_instance_uid': [
            f'Job not find for {runnable}, source_series_instance_uid={series_instance_uid}']}
        raise ValidationError(error_detail)

    return jobs.first()


class JobWithoutConstraintValidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['series_instance_uid', 'study_instance_uid', 'runnable']
        extra_kwargs = {
            'slurm_id': {'validators': []}  # This disables any validators, including the unique one
        }

    def run_validators(self, value):
        # We ignore the validations rules (such as unique_together)
        pass
