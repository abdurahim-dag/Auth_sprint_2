import uuid

from authlib.integrations.flask_client.apps import FlaskOAuth2App
from flask import abort
from flask import current_app
from flask import request
from flask import url_for
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import decode_token
from flask_restx import Namespace
from flask_restx import Resource

from app.models import UserSocial
from app.services.db import accounting
from app.services.db import add_model
from app.services.db import save_jti
from app.services.db import user_add
from app.services.db import user_get_by_email_nickname
from app.services.oauth import oauth as service
from app.utils import response_generate

from app.limiter import limiter

oauth = Namespace('oauth', 'API for accounting endpoints.' )

parser = oauth.parser()
parser.add_argument('social', type=str, required=True)


@oauth.route('/login')
class Login(Resource):
    decorators = [limiter.limit("20/minute")]

    @oauth.expect(parser)
    def get(self):
        args = parser.parse_args()
        social = args['social']
        redirect_uri = url_for('api.oauth_authorize', social=social, _external=True)
        return service.create_client(social).authorize_redirect(redirect_uri)


@oauth.route('/authorize')
class Authorize(Resource):
    decorators = [limiter.limit("20/minute")]

    @oauth.expect(parser)
    def get(self):
        args = parser.parse_args()
        social = args['social']

        client: FlaskOAuth2App = service.create_client(social)
        token = client.authorize_access_token()
        resp = client.get('info', token=token)
        resp.raise_for_status()

        profile = resp.json()
        if not profile:
            abort(400, 'unable to get profile')

        social_id = profile.get('id')
        if not social_id:
            abort(400, 'unable to get ID')

        result = dict()

        social_login = profile.get('login', f"User-{str(uuid.uuid4())}")
        social_email = profile.get('default_email', f"{str(uuid.uuid4())}@movie.app")

        user = user_get_by_email_nickname(social_email, social_login)

        if not user:
            result['attention'] = 'Проверьте Ващи данные и поменяйте пароль'
            user = user_add(social_login, social_email, str(uuid.uuid4()), status=True)
            add_model(
                UserSocial(
                    id=social_id,
                    email=social_email,
                    login=social_login,
                    user_id=user.id
                )
            )

        # Лог успешного входа в журнал.
        accounting(user.id, 'login', f"User agent: {request.user_agent}")

        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        ttl = current_app.config['JWT_REFRESH_TOKEN_EXPIRES'].total_seconds()
        # Запомним выданные refresh токены.
        save_jti(user.id, decode_token(refresh_token)['jti'], int(ttl))

        return response_generate(access_token, refresh_token, 'login')
