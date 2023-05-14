"""Тест ручек API ролей."""
import json
import os
from http import HTTPStatus


url_login = 'http://auth:5000/auth/api/v1/accounts/login'
users = json.loads(open(os.path.join('tests', 'functional', 'testdata', 'users.json'), 'rt', encoding='utf-8').read())


def test_not_admin_access_rights(db_init, make_get_request):
    body = users['users'][0]
    response = make_get_request(url_login, body=body, method='POST')

    assert response.status_code == HTTPStatus.OK

    url = 'http://auth:5000/auth/api/v1/roles'
    response = make_get_request(url, cookies=response.cookies, method='GET')

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_admin_access(db_init, make_get_request):
    body = users['admins'][0]
    response = make_get_request(url_login, body=body, method='POST')

    assert response.status_code == HTTPStatus.OK

    url = 'http://auth:5000/auth/api/v1/roles'
    response = make_get_request(url, cookies=response.cookies, method='GET')

    assert response.status_code == HTTPStatus.OK
