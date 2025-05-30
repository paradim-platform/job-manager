# Generated by Django 4.2.18 on 2025-04-24 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0010_alter_job_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='state',
            field=models.CharField(choices=[('APP_ERROR', 'The application encountered an unexpected error'), ('CANCELLED', 'The job was cancelled.'), ('TECHNICAL_ERROR', 'Error due to the platform, please contact PARADIM maintainers.'), ('FINISHED', 'Successful'), ('RUNNING', 'Running'), ('SUBMITTED_TO_SLURM', 'Submitted to Slurm'), ('SUBMITTED_TO_QUEUE', 'Submitted to Queue')], max_length=64),
        ),
    ]
