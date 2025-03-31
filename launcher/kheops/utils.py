def find_patient_id(study_tags: dict) -> str:
    try:
        return study_tags['00100020']['Value'][0]
    except KeyError:
        return ''


def find_patient_name(study_tags: dict) -> str:
    try:
        return study_tags['00100010']['Value'][0]['Alphabetic']
    except KeyError:
        return ''


def find_study_date(study_tags: dict) -> str:
    try:
        dicom_date = study_tags['00080020']['Value'][0]
        # ex. 19940423 -> 1994-04-23
        return f'{dicom_date[:4]}-{dicom_date[4:6]}-{dicom_date[6:8]}'
    except KeyError:
        return ''


def find_modalities(study_tags: dict) -> list[str]:
    """Returns modalities (sometimes, a modality is mark as None)"""
    return [i.upper().strip('"').strip() for i in study_tags['00080061']['Value'] if i is not None]


def find_study_uid(study_tags: dict) -> str:
    return study_tags['0020000D']['Value'][0]


def find_study_description(study_tags: dict) -> str:
    try:
        return study_tags['00081030']['Value'][0]
    except KeyError:
        return ''


def find_series_uid(series_tags: dict) -> str:
    return series_tags['0020000E']['Value'][0]


def find_series_description(series_tags: dict) -> str:
    try:
        return series_tags['0008103E']['Value'][0]
    except KeyError:
        return ''


def find_modality(series_tags: dict) -> str:
    return series_tags['00080060']['Value'][0]
