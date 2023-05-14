"""Тест ручки API поиска по фильмам."""
import json
from http import HTTPStatus

import pytest

from functional.models import Film, FilmDetail, GenreDetail
from functional.settings import film_index, genre_index, settings


@pytest.mark.parametrize('random_line',[film_index.data_file_path], indirect=True)
@pytest.mark.asyncio
async def test_search_film_by_title(es_init, random_line, make_get_request):
    """Тест поиска записи по фразе и N записей."""
    # Выбираем рандомный фильм из исходных тестовых данных.
    film_dict = json.loads(random_line)
    film = Film(**film_dict)
    page_num = 1
    page_size = 10
    params ={
        'page[number]': page_num,
        'page[size]': page_size,
        'query': film.title,
    }
    url = settings.api_endpoint_films + 'search'

    response = await make_get_request(url, params=params)
    len_resp = len(response.json)

    assert response.status == HTTPStatus.OK
    assert len_resp == page_size or len_resp > 0


@pytest.mark.parametrize('random_line',[film_index.data_file_path], indirect=True)
@pytest.mark.asyncio
async def test_search_film_cached(es_init, es_client, random_line, make_get_request):
    """Тест поиска записи с учётом кеша в Redis."""
    # Выбираем рандомный фильм из исходных тестовых данных.
    film_dict = json.loads(random_line)
    film = Film(**film_dict)
    params ={
        'query': film.title,
    }
    url = settings.api_endpoint_films + 'search'
    doc = {
        "doc": {'title': 'Unexpected'}
    }

    # Получаем список фильмов из API
    response = await make_get_request(url, params=params)

    assert response.status == HTTPStatus.OK
    assert len(response.json) > 0

    # Выбираем первый
    film_api_first = Film(**response.json[0])

    # Обновляем запись об этом фильме в ES.
    await es_client.update(index=film_index.index_name, id=film.id, body=doc)

    # Вновь забираем фильм из API, ожидая, что мы берём его из кэша.
    response = await make_get_request(url, params=params)
    film_api_second = Film(**response.json[0])

    # Сравниваем результат с предыдущим
    assert film_api_first.dict() == film_api_second.dict()

@pytest.mark.parametrize('random_line',[genre_index.data_file_path], indirect=True)
@pytest.mark.asyncio
async def test_film_by_genre_name(es_init, random_line, make_get_request):
    """Тест поиска конкретного фильма, по названию жанра."""
    # Выбираем рандомный жанр из исходных тестовых данных.
    genre_dict = json.loads(random_line)
    genre = GenreDetail(**genre_dict)
    url = settings.api_endpoint_films + f"search/?filter[genre.name]={genre.name}"

    # Запрашиваем по имени жанра из api поиска фильмы.
    response = await make_get_request(url)
    films = response.json

    # Важен сам факт наличия фильмов, так как поиск по имени жанру полнотекстовый.
    # И не всегда имя жанра будет совпадать с искомым, так поиск по Sport даст и фильмы с жанром Short.
    assert response.status == HTTPStatus.OK
    assert len(films) > 0


@pytest.mark.parametrize('random_line',[genre_index.data_file_path], indirect=True)
@pytest.mark.asyncio
async def test_film_by_genre_id(es_init, random_line, make_get_request):
    """Тест поиска конкретного фильма, по названию жанра."""
    # Выбираем рандомный жанр из исходных тестовых данных.
    genre_dict = json.loads(random_line)
    genre = GenreDetail(**genre_dict)
    url = settings.api_endpoint_films + f"search/?filter[genre]={genre.id}"

    # Запрашиваем по имени жанра из api поиска фильмы.
    response = await make_get_request(url)
    films = response.json

    assert response.status == HTTPStatus.OK
    assert len(films) > 0

    # Здесь же обязательно присутствие жанра (id) во всех результатах.
    for film in films:
        obj = Film(**film)
        url = settings.api_endpoint_films + str(obj.id)

        response = await make_get_request(url)

        assert response.status == HTTPStatus.OK

        obj_api = FilmDetail(**response.json)
        genres_api = obj_api.genre
        genres_name_api = [g.name for g in genres_api if g.id == genre.id]

        assert len(genres_name_api) > 0
