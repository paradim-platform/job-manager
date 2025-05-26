from fnmatch import fnmatch

from launcher import kheops
from launcher.kheops import client_api


def retrieve_series(
        album_id: str,
        access_token: str,
        modality: str,
        study_date_filter: str | None = None,
        series_description_filter: str | None = None) -> list[kheops.Series]:
    study_date_filter = '*' if study_date_filter is None else study_date_filter.replace('-', '')
    series_description_filter = '*' if series_description_filter is None else series_description_filter

    series_in_album = client_api.get_series_in_album(album_id, modality)

    return [
        s for s in series_in_album
        if (
                s.modality == modality and
                fnmatch(s.description, series_description_filter) and
                fnmatch(s.study.date, study_date_filter)
        )
    ]
