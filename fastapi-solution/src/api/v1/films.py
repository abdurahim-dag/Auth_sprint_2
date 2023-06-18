from http import HTTPStatus
from typing import List
from typing import Union
from uuid import UUID

from auth import auth
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from models import Film
from models import FilmDetail
from models.messages import Film as Message
from services import FilmService
from services import cache
from services import get_film_service

from .qparams import FilmParams


router = APIRouter()


@router.get(
    '',
    response_model=List[Union[Film, FilmDetail]],
    summary='Главная страница фильмов.',
    description='На ней выводятся популярные фильмы, с указанием поля сортировки и жанра.',
    response_description="Список фильмов.",
)
@cache()
async def film_list(
        film_service: FilmService = Depends(get_film_service),
        roles: list = Depends(auth(['premium'])),
        params: FilmParams = Depends(),
        message: Message = Depends(),
) -> List[Union[Film, FilmDetail]]:
    if roles:
        film_service.model = FilmDetail
    films = await film_service.get_list(params)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=message.not_founds)
    # Генерим json, т.к. в films будут Film или FilmDetail
    json_compatible_item_data = jsonable_encoder(films)
    return JSONResponse(content=json_compatible_item_data)

@router.get(
    '/search',
    response_model=list[Film],
    summary='Полнотекстовый поиск по фильмам.',
    description='''
    Полнотекстовый поиск фильма, по указанному параметру query в запросе.
    ''',
    response_description="Список фильмов.",
)
@cache()
async def film_list_search(
        film_service: FilmService = Depends(get_film_service),
        params: FilmParams = Depends(),
        message: Message = Depends()
) -> list[Film]:
    films = await film_service.get_list(params)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=message.not_founds)
    return films


@router.get(
    '/{film_id}',
    response_model=FilmDetail,
    summary='Информация о фильме.',
    description='Детальная информация о фильме.',
    response_description='Фильм с информацией по всем имеющимися полям.',
)
@cache()
async def film_detail(
        film_id: UUID = Query(description='ID фильма.'),
        film_service: FilmService = Depends(get_film_service),
        message: Message = Depends()
) -> FilmDetail:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=message.not_found)
    return film
