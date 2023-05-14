"""Тест ручки API, для персон."""
from http import HTTPStatus

from app.services.db import user_confirmed_email
from app.services.db import user_get_by_email


def test_signup(db_init, make_get_request):
    url = 'http://auth:5000/auth/api/v1/users/signup'
    test_user = {
        'nickname': 'test_user1',
        'email': 'test_user1@email',
        'password': 'TestUserPassword'
    }

    response = make_get_request(url, body=test_user, method='POST')

    assert response.status_code == HTTPStatus.CREATED

    user = user_get_by_email(test_user['email'])

    assert user is not None

    user_confirmed_email(user.id)
    url = 'http://auth:5000/auth/api/v1/accounts/login'
    response = make_get_request(url, body=test_user, method='POST')

    assert response.status_code == HTTPStatus.OK
