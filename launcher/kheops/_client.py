from http import HTTPStatus

import httpx
from django.conf import settings

from .models import Album, Series, Study


class KheopsClient:

    def __init__(self, url: str):
        self.url = url

    def retrieve_albums(self, access_token: str) -> list[Album]:
        response = httpx.get(
            url=f'{self.url}/api/albums',
            timeout=60,
            headers={'Authorization': f'Bearer {access_token}'}
        )

        if response.status_code == 200:
            return [
                Album(
                    label=album['name'],
                    id_=album['album_id'],
                    description=album['description'],
                    modalities=album['modalities'],
                    number_of_studies=album['number_of_studies'],
                    number_of_series=album['number_of_series'],
                ) for album in response.json()]

        return []

    def can_user_add_series_to_album(self, album: Album, access_token: str) -> bool:
        response = httpx.get(
            url=f'{self.url}/api/albums/{album.id_}',
            timeout=60,
            headers={'Authorization': f'Bearer {access_token}'}
        )

        if response.status_code == HTTPStatus.OK:
            result = response.json()
            able_to_add_series = result['add_series']
            is_admin = result['is_admin']

            return is_admin or able_to_add_series

        return False


class KheopsApiClient:

    def __init__(self, url: str):
        self.url = url

    def get_series_in_album(self, album_id: str, modality: str | None = None) -> list[Series]:
        url = f'{self.url}/album-content/{album_id}'
        if modality is not None:
            url += f'?modality={modality}'

        response = httpx.get(url=url, timeout=300)  # 5 mins

        if response.status_code == HTTPStatus.OK:
            data = response.json()

            studies = []
            seriess = []

            for study_data in data['studies']:
                study_series = []
                patient_id = study_data['patient_id']
                patient_name = study_data['patient_name']
                date = study_data['study_date']
                description = study_data['study_description']

                study = Study(
                    uid=study_data['study_uid'],
                    patient_id='' if patient_id is None else patient_id,
                    patient_name='' if patient_name is None else patient_name,
                    date='' if date is None else date.replace('-', ''),
                    description='' if description is None else description,
                    modalities=[],  # This is set afterward
                )
                studies.append(study)

                for series_data in study_data['series']:
                    description = series_data['series_description']

                    study_series.append(
                        Series(
                            uid=series_data['series_uid'],
                            description='' if description is None else description,
                            modality=series_data['modality'],
                            study=study
                        )
                    )

                study.modalities = list({s.modality for s in study_series})

                seriess += study_series

            return seriess

        return []


client = KheopsClient(settings.KHEOPS_URL)
client_api = KheopsApiClient(settings.KHEOPS_API_URL)
