from flask_restx import fields


def register_models_account(api):
    api.model('UserAccount', {
        'email': fields.String,
        'password': fields.String,
    })
    api.model('UserLogin', {
        'login': fields.Boolean
    })


def register_models_user(api):
    api.model('UserNew', {
        'nickname': fields.String,
        'email': fields.String,
        'status': fields.Boolean,
        'password': fields.String,
    })
    api.model('UserPassword', {
        'password': fields.String
    })


def register_models_role(api):
    api.model('Role', {
        'id': fields.Integer,
        'name': fields.String,
    })
    api.model('RoleNew', {
        'name': fields.String,
    })


def jwt_parser(api):
    parser = api.parser()
    parser.add_argument('access_token_cookie', location='cookies', required=True)
    parser.add_argument('refresh_token_cookie', location='cookies', required=True)
    parser.add_argument('csrf_refresh_token', location='cookies', required=True)
    parser.add_argument('csrf_access_token', location='cookies', required=True)
    return parser


def cors_header(api):
    parser = api.parser()
    parser.add_argument('X-CSRF-TOKEN', location='headers', required=True, help='Необходим токен JWT')
    return parser
