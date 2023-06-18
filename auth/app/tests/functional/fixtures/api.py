"""Фикстуры для работы с ручками."""
import pytest
import requests
from requests.structures import CaseInsensitiveDict


@pytest.fixture
def make_get_request():
    """Собственно запрос к API посредством aiohttp сессии."""
    def go(url, params=None, body=None, cookies = None, method = 'GET'):
        response: requests.Response
        headers: CaseInsensitiveDict = CaseInsensitiveDict(data={
            'X-Request-Id': 'test'
        })

        # Для ручек требующих авторизацию необходимо в запросах указать csrf_refresh_token
        if cookies:
            csrf_refresh_token = cookies.get('csrf_refresh_token', None)

            if csrf_refresh_token:
                headers['X-CSRF-TOKEN'] = csrf_refresh_token

        response = requests.request(
            method,
            url,
            params=params,
            allow_redirects=True,
            json=body,
            cookies=cookies,
            headers=headers
        )
        response.json = response.json()

        return response

    return go
