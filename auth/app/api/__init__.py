from flask import Blueprint
from app.api.v1 import namespaces as api_v1_namespaces


api_v1_blueprint = Blueprint('api', __name__, url_prefix='/auth/api/v1')

