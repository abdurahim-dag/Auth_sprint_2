import http
import json
import logging

import redis
from flask import Flask
from flask import Response
from flask import jsonify
from flask import request
from flask_restx import Api
from sqlalchemy import create_engine
from werkzeug.exceptions import HTTPException

import app.db
from app import config
from app.limiter import limiter_register
from app.services.jwt import jwt
from app.services.oauth import init_oauth
from app.tracer import set_instrument_app


def create_app():
    config.settings = config.Settings()

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config.settings)

    limiter_register(app)

    db.engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    db.engine.execution_options(autocommit=False)
    db.redis = redis.Redis(host=config.settings.redis_host, port=config.settings.redis_port, decode_responses=True)

    jwt.init_app(app)
    init_oauth(app)

    if not app.debug:
        app.logger.setLevel(logging.WARNING)

    from app.api import api_v1_blueprint, api_v1_namespaces
    from app.superuser import superuser

    api = Api(
        api_v1_blueprint,
        title='Openapi swagger',
        version='1.0',
        description='A description endpoints api.',
        validate=True
    )
    for namespace in api_v1_namespaces:
        api.add_namespace(namespace)

    app.register_blueprint(api_v1_blueprint)
    app.register_blueprint(superuser)

    @app.errorhandler(HTTPException)
    def all_exception_handler(error: HTTPException):
        res = {error.name: error.description}
        return Response(status=error.code, mimetype="application/json", response=json.dumps(res))

    @app.errorhandler(Exception)
    def handle_internal_server_error(error):
        logging.exception(error)
        response = jsonify({'error': str(error)})
        response.status_code = 500
        return response

    jwt._set_error_handler_callbacks(api)

    @jwt.unauthorized_loader
    def unauthorized(msg):
        return {}, http.HTTPStatus.UNAUTHORIZED

    @app.before_request
    def before_request():
        request_id = request.headers.get('X-Request-Id')
        if not request_id:
            raise RuntimeError('request id is required')

    set_instrument_app(app)

    return app
