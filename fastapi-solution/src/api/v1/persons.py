from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import Request
from fastapi.responses import RedirectResponse

from models import Film
from models import PersonDetail
from models.messages import Person as Message
from services import PersonService
from services import cache
from services import get_person_service
from .qparams import CommonParams


router = APIRouter()


@router.get(
    '/search',
    response_model=list[PersonDetail],
    summary='Полнотекстовый поиск по персонам.',
    description='''
    Полнотекстовый поиск по персонам, по указанному параметру query в запросе.
    ''',
    response_description='Список персон.',
)
@cache()
async def film_list_search(
        person_service: PersonService = Depends(get_person_service),
        params: CommonParams = Depends(),
        message: Message = Depends()
) -> list[PersonDetail]:
    persons = await person_service.get_list(params)
    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=message.not_founds)
    return persons


@router.get(
    '/{person_id}',
    response_model=PersonDetail,
    summary='Информация о персоне.',
    description='Детальная информация о персоне.',
    response_description='Информация со всеми имеющимися полями о персоне.',
)
@cache()
async def person_detail(
        person_id: UUID = Query(description='ID персоны.'),
        person_service: PersonService = Depends(get_person_service),
        message: Message = Depends()
) -> PersonDetail:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=message.not_found)
    return person


@router.get(
    '/{person_id}/film',
    response_model=list[Film],
    summary='Информация о фильмах.',
    description='Детальная информация о фильмах связанных с персоной.',
    response_description='Фильм с информацией по всем имеющимися полям или сама персона.',
)
async def person_film(
        request: Request,
        person_id: UUID = Query(description='ID персоны.'),
        person_service: PersonService = Depends(get_person_service),
        message: Message = Depends()
) -> PersonDetail | RedirectResponse:
    person: PersonDetail = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=message.not_found)
    ids = [str(film_id) for film_id in person.film_ids]
    query_str = ''
    for _id in ids:
        q = f"ids={_id}"
        query_str += '&' + q
    if query_str:
        query_str = '?' + query_str[1:]
        app = request.app
        url = app.url_path_for('film_list_search')
        url += query_str
        return RedirectResponse(url)
    return person
