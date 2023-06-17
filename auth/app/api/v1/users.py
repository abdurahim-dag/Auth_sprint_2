from http import HTTPStatus

from flask import request
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_restx import Namespace
from flask_restx import Resource
from sqlalchemy.exc import IntegrityError

from app.models import Messages
from app.restx import jwt_parser
from app.restx import register_models_user
from app.services.db import confirm_token
from app.services.db import delete_role
from app.services.db import set_role
from app.services.db import user_add
from app.services.db import user_change_password
from app.services.rbac import role_required

from app.limiter import limiter


user = Namespace('users', 'API for accounting endpoints.' )

register_models_user(user)


@user.route('/signup')
class Signup(Resource):
    decorators = [limiter.limit("20/minute")]

    @user.expect(user.models['UserNew'])
    @user.doc(responses={HTTPStatus.OK.value: 'Success'})
    def post(self):
        """Ручка регистрации пользователя."""
        data = request.get_json(cache=False)

        nickname = data.get('nickname')
        email = data.get('email')
        password = data.get('password')

        # Пытаемся добавить пользователя.
        # И реагируем на ошибки добавления:
        #  nickname или email уже есть, и другие ошибки валидации.
        try:
            user_add(nickname, email, password)
        except IntegrityError as e:
            return {'message': Messages.login_exist}, HTTPStatus.NOT_FOUND
        except ValueError as e:
            return {'message': str(e)}, HTTPStatus.NOT_FOUND

        return {'message': 'ok'}, HTTPStatus.CREATED


@user.route('/confirm_email/<uuid:token>')
class ConfirmEmail(Resource):
    decorators = [limiter.limit("20/minute")]

    @user.doc(params={'token': 'An UUID'})
    @user.doc(responses={HTTPStatus.OK.value: 'Success'})
    def get(self, token):
        """Ручка подтверждения email по выданному токену."""
        try:
            confirm_token(token)
        except Exception as e:
            return {'message': str(e)}, HTTPStatus.NOT_FOUND

        return {'message': Messages.user_email_confirmed}, HTTPStatus.OK


@user.route("/change_password", methods=["POST"])
@user.expect(jwt_parser(user))
class ChangePassword(Resource):
    decorators = [jwt_required(refresh=True)]

    @user.expect(user.models['UserPassword'])
    def post(self):
        """Ручка изменения пароля."""
        password = request.json.get("password", '')

        try:
            user_change_password(get_jwt_identity(), password)
        # Ошибки валидации.
        except ValueError as e:
            return {'message': str(e)}, HTTPStatus.NOT_FOUND

        return {'password changed': True}, HTTPStatus.OK


# Ручка доступна только админам.
@user.route("/<int:id>/role/<int:role>")
@user.expect(jwt_parser(user))
class Role(Resource):
    decorators = [role_required(['admin']), jwt_required(refresh=True)]

    @user.doc(params={'id': 'Id of user', 'role': 'Id of Role'})
    @user.doc(responses={HTTPStatus.NO_CONTENT.value: 'Success'})
    def post(self, id, role):
        """Ручка добавления роли к пользователю."""
        set_role(id, role)
        return {'msg': 'Role added!'}, HTTPStatus.NO_CONTENT

    @user.doc(params={'id': 'Id of user', 'role': 'Id of Role'})
    @user.doc(responses={HTTPStatus.NO_CONTENT.value: 'Success'})
    def delete(self, id, role):
        """Ручка удаления роли у пользователя."""
        delete_role(id, role)
        return {'msg': 'Role added!'}, HTTPStatus.NO_CONTENT
