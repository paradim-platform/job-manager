from rest_framework import serializers


class RunnableSerializer(serializers.Serializer):
    modality = serializers.CharField()
    series_instance_uid = serializers.CharField()
    study_instance_uid = serializers.CharField()

    album_id = serializers.CharField(required=False)
    app_name = serializers.CharField(required=False)
    app_version = serializers.CharField(required=False)
