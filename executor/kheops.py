import json
from http import HTTPStatus

import httpx

from .config import KHEOPS_API_URL
from .logs import logger


class KheopsAPIClient:

    def __init__(self, url: str):
        self.url = url

    def copy_series_to_target_album(self, generated_series_uid: str, target_album_id: str):
        logger.debug(f'Adding {generated_series_uid=} to {target_album_id=}.')
        response = httpx.put(
            url=f'{self.url}/add-series/',
            data={
                'series_instance_uid': generated_series_uid,
                'target_album_id': target_album_id
            }
        )

        if response.status_code == HTTPStatus.OK:
            logger.info(f'Generated Series {generated_series_uid} added to album {target_album_id}')
        else:
            try:
                error_message = response.json()
            except json.JSONDecodeError:
                error_message = response.text

            logger.error(
                f'Failed to copy generated series {generated_series_uid} to album {target_album_id}. '
                f'Error message: {error_message}.'
            )


client = KheopsAPIClient(KHEOPS_API_URL)
