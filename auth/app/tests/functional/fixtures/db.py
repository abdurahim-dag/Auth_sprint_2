"""Модуль фикстур, для работы с БД."""
import json
import os.path
from typing import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import Session

import app.config
import app.db
from app.models import Role
from app.services.db import insert_model
from app.services.db import set_role
from app.services.db import user_add


@pytest.fixture(scope='session')
def db_engine() -> Generator[None, None, None]:
    """Установим движок sqlalchemy, для тестов."""
    settings = app.config.settings
    app.db.engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
    app.db.engine.execution_options(autocommit=False)

    try:
        yield
    finally:
        # Очистим таблицы БД.
        with Session(app.db.engine) as session:
            sql = text("""
                truncate auth.role CASCADE;
                truncate auth.user CASCADE;
            """)
            session.execute(sql)
            session.commit()


@pytest.fixture(scope='session')
def db_init(db_engine):
    """Инициализацируем БД тестовыми данными."""
    users = json.loads(open(os.path.join('tests', 'functional','testdata', 'users.json'), 'rt', encoding='utf-8').read())
    roles = json.loads(open(os.path.join('tests', 'functional','testdata', 'roles.json'), 'rt', encoding='utf-8').read())
    admin_user = None
    admin_role = None
    for user in users['users'] + users['admins']:
        u = user_add(user['nickname'], user['email'], user['password'], status=user['status'])
        if u.nickname == 'admin':
            admin_user = u
    for role in roles:
        r = insert_model(role, Role)
        if r.name == 'admin':
            admin_role = r
    set_role(admin_user.id, admin_role.id)

    # Продолжим наши тесты.
    yield
