from django.core.exceptions import ValidationError
from django.db import models


def validate_no_space(value: str) -> None:
    if ' ' in value:
        raise ValidationError('App name should not contain spaces.')


class Modality(models.Model):
    abbreviation = models.CharField(max_length=64, unique=True, verbose_name="Modality abbreviation")
    long_name = models.CharField(max_length=255, verbose_name="Modality name")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'Modality({self.abbreviation}, {self.long_name}, active={self.is_active})'


class Level(models.Model):
    PATIENT = 'Patient'
    STUDY = 'Study'
    SERIES = 'Series'
    _LEVEL_CHOICES = [
        (PATIENT, 'Patient'),
        (STUDY, 'Study'),
        (SERIES, 'Series'),
    ]

    value = models.CharField(max_length=30, choices=_LEVEL_CHOICES, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'Level({self.value}, active={self.is_active})'


class App(models.Model):
    name = models.CharField(max_length=64, unique=True, validators=[validate_no_space])
    description = models.CharField(max_length=255)
    automatic_run = models.BooleanField(verbose_name='Automatic run to new stable series in Orthanc.', default=False)

    def __str__(self):
        return f'App({self.name}, {self.description})'


class Size(models.Model):
    XS = 'XS'
    S = 'S'
    S_fast = 'S_fast'
    M = 'M'
    M_fast = 'M_fast'
    L = 'L'
    L_fast = 'L_fast'
    XL = 'XL'
    XL_fast = 'XL_fast'
    XXL = 'XXL'
    XXL_fast = 'XXL_fast'
    _SIZE_CHOICES = [
        (XS, 'XS'),
        (S, 'S'),
        (S_fast, 'S_fast'),
        (M, 'M'),
        (M_fast, 'M_fast'),
        (L, 'L'),
        (L_fast, 'L_fast'),
        (XL, 'XL'),
        (XL_fast, 'XL_fast'),
        (XXL, 'XXL'),
        (XXL_fast, 'XXL_fast'),
    ]

    abbreviation = models.CharField(max_length=8, choices=_SIZE_CHOICES, unique=True)

    def __str__(self):
        return f'Size({self.abbreviation})'


class Runnable(models.Model):
    app = models.ForeignKey(App, on_delete=models.DO_NOTHING)
    modality = models.ForeignKey(Modality, on_delete=models.DO_NOTHING)
    version = models.CharField(max_length=255)
    level = models.ForeignKey(Level, on_delete=models.DO_NOTHING)
    with_gpu = models.BooleanField(default=False)
    size = models.ForeignKey(Size, on_delete=models.DO_NOTHING)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['app', 'version']

    def __str__(self):
        return f'{self.app.name}:{self.version} [{self.modality.abbreviation}]'
