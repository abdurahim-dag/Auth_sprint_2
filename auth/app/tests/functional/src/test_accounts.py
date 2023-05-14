"""Тест ручки API, для accounts."""
import json
import os
from http import HTTPStatus


url_login = 'http://auth:5000/auth/api/v1/accounts/login'
users = json.loads(open(os.path.join('tests', 'functional', 'testdata', 'users.json'), 'rt', encoding='utf-8').read())
body = users['users'][0]

def test_correct_login(db_init, make_get_request):
    response = make_get_request(url_login, body=body, method='POST')

    assert response.status_code == HTTPStatus.OK


def test_incorrect_login(db_init, make_get_request):
    body['password'] = 'incorrect'
    response = make_get_request(url_login, body=body, method='POST')

    assert response.status_code == HTTPStatus.UNAUTHORIZED
