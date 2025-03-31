from datetime import datetime

from django.core.cache import cache

from .utils import CACHE_RETENTION


def init_aggregation_cache(user_id: str, album_id: str, series_description_filter: str, output_format: str) -> None:
    results_key = _make_aggregation_results_cache_key(user_id)
    results = cache.get(results_key, {})

    # Marking the file as running
    result_key = _make_aggregation_result_cache_key(user_id, album_id, series_description_filter, output_format)
    results[result_key] = 'running'

    cache.set(results_key, results, CACHE_RETENTION)


def retrieve_aggregation_results_cache(user_id: str) -> dict:
    results_key = _make_aggregation_results_cache_key(user_id)

    return cache.get(results_key, {})


def retrieve_aggregation_result_cache(user_id: str, album_id: str, series_description_filter: str, output_format: str) -> dict:
    results_key = _make_aggregation_results_cache_key(user_id)
    result_key = _make_aggregation_result_cache_key(user_id, album_id, series_description_filter, output_format)

    results = cache.get(results_key, {})
    result = results.get(result_key, None)

    return result


def set_as_running(user_id: str, album_id: str, series_description_filter: str, output_format: str) -> None:
    results_key = _make_aggregation_results_cache_key(user_id)
    results = cache.get(results_key, {})

    # Marking the file as running
    result_key = _make_aggregation_result_cache_key(user_id, album_id, series_description_filter, output_format)
    results[result_key] = 'running'

    cache.set(results_key, results, CACHE_RETENTION)


def set_result(user_id: str, album_id: str, series_description_filter: str, output_format: str, result: str) -> None:
    results_key = _make_aggregation_results_cache_key(user_id)
    results = cache.get(results_key, {})

    # Setting the result
    result_key = _make_aggregation_result_cache_key(user_id, album_id, series_description_filter, output_format)
    results[result_key] = result

    cache.set(results_key, results, CACHE_RETENTION)


def _make_aggregation_results_cache_key(user_id: str) -> str:
    return f'aggregation_result_{user_id}'


def _make_aggregation_result_cache_key(user_id: str, album_id: str, series_description_filter: str, output_format: str) -> str:
    result_key = f"aggregation_result_{user_id}_{album_id}_{series_description_filter}_{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.{output_format}"

    return result_key
