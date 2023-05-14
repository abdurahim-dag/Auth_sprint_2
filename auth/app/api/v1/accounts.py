from http import HTTPStatus

from flask import current_app
from flask import request
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import decode_token
from flask_jwt_extended import get_jwt
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_restx import Namespace
from flask_restx import Resource

from app.models import Messages
from app.restx import cors_header
from app.restx import jwt_parser
from app.restx import register_models_account
from app.services.db import accounting
from app.services.db import delete_jti
from app.services.db import revoke_jtis
from app.services.db import save_jti
from app.services.db import user_get_by_email
from app.utils import response_generate


account = Namespace('accounts', 'API for accounting endpoints.' )

register_models_account(account)


@account.route("/login")
class Login(Resource):

    @account.expect(account.models['UserAccount'])
    @account.doc(responses={HTTPStatus.OK.value: 'Success'}, model=account.models['UserLogin'])
    def post(self):
        """Ручка логина."""
        email = request.json.get("email", '')
        password = request.json.get("password", '')

        # Проверим email, статус подтверждения и пароль.
        user = user_get_by_email(email)
        if not user or not user.status or not user.check_password(password):
            return {"msg": Messages.login_fail}, HTTPStatus.UNAUTHORIZED

        # Лог успешного входа в журнал.
        accounting(user.id, 'login', f"User agent: {request.user_agent}")

        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        ttl = current_app.config['JWT_REFRESH_TOKEN_EXPIRES'].total_seconds()
        # Запомним выданные refresh токены.
        save_jti(user.id, decode_token(refresh_token)['jti'], int(ttl))

        return response_generate(access_token, refresh_token, 'login')


@account.route("/refresh")
@account.expect(jwt_parser(account))
class Refresh(Resource):
    decorators = [jwt_required(refresh=True)]

    @account.doc(responses={HTTPStatus.OK.value: 'Success'})
    def post(self):
       """Ручка обновления токенов."""
       identity = get_jwt_identity()

       access_token = create_access_token(identity=identity)
       refresh_token = create_refresh_token(identity=identity)

       # Удалим ранее запомненный refresh токен.
       delete_jti(identity, get_jwt()["jti"])
       ttl = current_app.config['JWT_REFRESH_TOKEN_EXPIRES'].total_seconds()
       # Запомним выданные refresh токены.
       save_jti(identity, decode_token(refresh_token)['jti'], int(ttl))

       return response_generate(access_token, refresh_token, 'token_refresh')


@account.route("/logout")
@account.expect(jwt_parser(account))
class Logout(Resource):
    decorators = [jwt_required(refresh=True)]

    @account.doc(parser=cors_header(account))
    @account.doc(responses={HTTPStatus.OK.value: 'Success'})
    def post(self):
        """Ручка выхода."""
        identity = get_jwt_identity()
        # Удалим ранее запомненный refresh токен.
        delete_jti(identity, get_jwt()["jti"])

        return {'logout': True}, HTTPStatus.OK


@account.route("/logout_others")
@account.expect(jwt_parser(account))
class LogoutOthers(Resource):
    decorators = [jwt_required(refresh=True)]

    @account.doc(responses={HTTPStatus.OK.value: 'Success'})
    def post(self):
        """Ручка выход со всех устройств."""
        identity = get_jwt_identity()
        revoke_jtis(identity, get_jwt()["jti"])

        return {'logout': True}, HTTPStatus.OK
