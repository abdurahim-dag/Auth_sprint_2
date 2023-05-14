import uuid

from flask import jsonify
from flask import url_for
from flask_jwt_extended import set_access_cookies
from flask_jwt_extended import set_refresh_cookies

from app.services.db import save_confirm_token


def confirm_url_generate(id):
    token = uuid.uuid4()
    save_confirm_token(token, id)
    return url_for('api.v1.users.confirm_email', _external=True, token=token)


def response_generate(access_token, refresh_token, answer):
    resp = jsonify({answer: True})
    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)
    return resp

def check_profile_id(profile):
    return 'id' not in profile


def check_profile_email(profile):
    return 'id' not in profile


def check_profile_login(profile):
    return 'id' not in profile
