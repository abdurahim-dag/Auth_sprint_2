import http
import json
import logging

import redis
from flask import Flask
from flask import Response
from flask_restx import Api
from sqlalchemy import create_engine
from werkzeug.exceptions import HTTPException

import app.db
import app.signals
from app import config
from app.services.jwt import jwt
from authlib.integrations.flask_client import OAuth
from app.services.oauth import init_oauth


def create_app(test_config=None):
    config.settings = config.Settings()

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config.settings)

    db.engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    db.engine.execution_options(autocommit=False)
    db.redis = redis.Redis(host=app.config['REDIS_HOST'], port=app.config['REDIS_PORT'], decode_responses=True)

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

    jwt._set_error_handler_callbacks(api)

    @jwt.unauthorized_loader
    def unauthorized(msg):
        return {}, http.HTTPStatus.UNAUTHORIZED

    return app
