from django.core.cache import cache

from launcher import kheops


def retrieve_user_albums(access_token: str, user_id: str) -> list[kheops.Album]:
    albums_key = f'albums_{user_id}'
    albums = cache.get(albums_key, [])

    if not albums:
        albums = kheops.client.retrieve_albums(access_token)
        cache.set(albums_key, albums)

    return albums
