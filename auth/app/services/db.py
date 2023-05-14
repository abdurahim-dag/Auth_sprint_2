"""Модуль с работой persistent databases."""
from functools import wraps
from typing import Any
from typing import Callable

from flask_sqlalchemy.pagination import SelectPagination
from redis import Redis
from sqlalchemy import delete
from sqlalchemy import insert
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from app.db import get_redis
from app.db import get_session
from app.models import AccountHistory
from app.models import Messages
from app.models import Role
from app.models import User
from app.models import UserRole


def set_session():
    """Декоратор, для всех обращений к PG, который создаёт и прокидывает сессию."""

    def wrapper(func: Callable):

        @wraps(func)
        def decorator(*args, **kwargs):

            session: Session
            with get_session() as session:
                res = func(*args, **kwargs, session=session)
                session.commit()
            return res

        return decorator

    return wrapper


@set_session()
def user_add(nickname, email, password, /, session: Session = None, status: bool = False) -> User:
    """Функция создаёт пользователя."""
    user = User(
        nickname=nickname,
        email=email,
        # Для некоторых тестов и cli создания суперюзера нужен статус=True.
        status=status
    )
    user.set_password(password=password)
    session.add(user)
    session.commit()
    # Для того, чтобы отдать модель наружу, нужно сделать detach.
    session.refresh(user)
    session.expunge(user)
    return user


@set_session()
def insert_model(instance: dict, model, /, session: Session = None) -> Any:
    """Функция добавления модели в БД."""
    id = session.execute(
        insert(model).returning(model.id),[
            instance
    ]).fetchone()
    # Для того, чтобы отдать модель наружу, нужно сделать detach.
    res = session.get(model, id)
    session.expunge(res)
    return res


@set_session()
def user_change_password(id, password, /, session: Session = None):
    """Процедура смены пароли в БД."""
    user = session.get(User, id)
    user.set_password(password=password)


@set_session()
def user_confirmed_email(id, /, session: Session = None):
    """Процедура смены статуса в БД."""
    user = session.get(User, id)
    if user:
        user.status = True
    else:
        raise NoResultFound(Messages.user_not_found)


@set_session()
def model_get(id, model, /, session: Session = None) -> Any | None:
    """Функция выборки модели из БД."""
    res = session.get(model, id)
    if res:
        session.expunge(res)
    return res


@set_session()
def model_list_paginated(model, page, /, session: Session = None) -> Any:
    """Функция, которая возвращает модели и параметры пагинации из БД."""
    paginated = SelectPagination(
        select=select(model),
        session=session,
        page=page,
        error_out=False,
        count=True,
    )
    # Для того, чтобы отдать модель наружу, нужно сделать detach.
    for item in paginated.items:
        session.expunge(item)
    return paginated


@set_session()
def user_get_by_email(email, /, session: Session = None) -> User | None:
    """Функция выборки User'а из БД."""
    user = session.execute(
        select(User).where(User.email == email)
    ).first()
    if user:
        session.expunge(user[0])
        user = user[0]
    return user


@set_session()
def accounting(user_id, type, params, /, session: Session = None):
    """Процедура журналирования события."""
    account = AccountHistory(
        user_id=user_id,
        type=type,
        params=params
    )
    session.add(account)


@set_session()
def patch_model(instance: dict, model, /, session: Session = None):
    session.execute(
        update(model),
        [ instance ]
    )


@set_session()
def delete_model(id, model, /, session: Session = None):
    session.execute(
        delete(model).where(model.id == id)
    )


@set_session()
def check_role_in_user(user_id, role_name, /, session: Session = None):
    """Проверим есть ли роль у пользователя."""
    role = (
        session.
        query(Role).
        where(Role.name == role_name).
        one()
    )
    user_role = (
        session.
        query(UserRole).
        where(UserRole.role_id == role.id, UserRole.user_id == user_id).
        first()
    )
    if user_role:
        return True
    else:
        return False


@set_session()
def set_role(user_id, role_id, /, session: Session = None):
    user = session.get(User, user_id)
    role = session.get(Role, role_id)
    user.roles.append(role)


@set_session()
def delete_role(user_id, role_id, /, session: Session = None):
    """Удалим связь между ролью и пользователем."""
    session.delete(
        session.
        query(UserRole).
        where(UserRole.role_id == role_id, UserRole.user_id == user_id).
        first()
    )


def set_client(func):
    """Декоратор установки клиента к Redis, для всех операций."""
    def wrapper(*args, **kwargs):
        client = get_redis()
        return func(*args, **kwargs, client=client)
    return wrapper


@set_client
def save_jti(user_id, jwt_id, ttl, /, client: Redis = None):
    # Составной ключ, для того чтобы затем их находить по id ключа или пользователя.
    key = f"{jwt_id}:user:{user_id}"
    client.set(key, '')
    client.expire(key, ttl)


@set_client
def delete_jti(user_id, jwt_id, /, client: Redis = None):
    key = f"{jwt_id}:user:{user_id}"
    client.delete(key)


@set_client
def revoke_jtis(user_id, jwt_id, /, client: Redis = None):
    """Выйти на остальных устройствах."""
    pattern = f"*:user:{user_id}"
    current_key = f"{jwt_id}:user:{user_id}"
    keys_to_delete = client.keys(pattern)
    for key in keys_to_delete:
        if current_key != key:
            client.delete(key)


@set_client
def check_jti(user_id, jwt_id, /, client: Redis = None):
    key = f"{jwt_id}:user:{user_id}"
    if client.get(key) is None:
        raise KeyError('Not founded key!')


@set_client
def save_confirm_token(token, id, /, client: Redis = None):
    """Сохраним токен подтверждения почты и id пользователя."""
    client.set(str(token), id)


@set_client
def confirm_token(token, /, client: Redis = None):
    """Удалим токен подтверждения и изменим статус пользователя по ключу."""
    token = str(token)
    id = client.get(token)
    if id:
        user_confirmed_email(id)
        client.delete(token)
    else:
        raise KeyError(Messages.token_not_found % (token))


@set_session()
def user_get_by_email_nickname(email, nickname, /, session: Session = None) -> User | None:
    """Функция выборки User'а из БД."""
    user = session.execute(
        select(User).where(User.email == email, User.nickname == nickname)
    ).first()
    if user:
        session.expunge(user[0])
        user = user[0]
    return user


@set_session()
def add_model(instance, /, session: Session = None) -> None:
    """Функция добавления модели в БД."""
    session.add(instance)
    session.commit()
