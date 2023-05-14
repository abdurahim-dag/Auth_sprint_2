"""Модуль, для работы с RBAC."""
from functools import wraps
from http import HTTPStatus
from typing import Callable

from flask import jsonify
from flask_jwt_extended import get_jwt
from flask_jwt_extended import get_jwt_identity
from flask import abort
from app.models import Messages
from app.services.db import check_role_in_user


def role_required(roles: list[str]):
    """Decorator function for endpoints that check allow."""

    def wrapper(func: Callable):

        @wraps(func)
        def decorator(*args, **kwargs):

            checked = False

            claims_roles = get_jwt().get('roles', None)
            if claims_roles and set(claims_roles) & set(roles):
                # Для админов перепроверим актуальность.
                if 'admin' in roles:
                    identity = get_jwt_identity()
                    if check_role_in_user(identity, 'admin'):
                        checked = True
                else:
                    checked = True

            if checked:
                return func(*args, **kwargs)
            else:
                abort(HTTPStatus.FORBIDDEN, Messages.forbidden)

        return decorator

    return wrapper
