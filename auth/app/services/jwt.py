"""Модуль работы с токенами JWT."""
from flask_jwt_extended import JWTManager
from sqlalchemy.orm import joinedload

from app.models import User
from app.services.db import check_jti
from app.services.db import get_session
from app.services.db import model_get


jwt = JWTManager()

# @jwt.user_identity_loader
# def user_identity_lookup(user):
#     return user.id


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return model_get(identity, User)


@jwt.additional_claims_loader
def add_claims_to_access_token(identity):
    # Засунем все роли пользователя в claims JWT.
    with get_session() as session:
        user = session.query(User).options(joinedload(User.roles)).filter_by(id=identity).one()
        return {
            "roles": [role.name for role in user.roles]
        }


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
    """Проверка на отыв refresh токена."""
    check = False
    jti = jwt_payload["jti"]
    id = jwt_payload["sub"]

    try:
        user = model_get(id, User)
        if user:
            check_jti(user.id, jti)
        else:
            check = True
    except KeyError:
        check = True

    return check
