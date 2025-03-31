from dataclasses import dataclass
from enum import Enum


@dataclass
class Album:
    label: str
    id_: str

    description: str
    modalities: list[str]

    number_of_studies: int
    number_of_series: int

    def __str__(self):
        return self.label


@dataclass
class Study:
    patient_id: str
    patient_name: str
    date: str
    modalities: list[str]
    uid: str
    description: str

    def __str__(self):
        modalities = '|'.join(self.modalities)
        return f'{self.patient_id} - {self.patient_name} ({self.description}, {modalities}, {self.date})'


@dataclass
class Series:
    uid: str
    description: str
    modality: str

    study: Study

    def __str__(self):
        return f'{self.modality} - {self.description}'


@dataclass
class Runnable:
    app: str
    version: str
    level: str
    modality: str
    size: str
    with_gpu: bool

    def __str__(self):
        return f'{self.app}:{self.version} - Modality={self.modality}'


class Level(Enum):
    ALBUM = 'album'
    STUDY = 'study'
    SERIES = 'series'
