from http import HTTPStatus

from flask import abort
from flask import request
from flask_jwt_extended import jwt_required
from flask_restx import Namespace
from flask_restx import Resource

from app.models import Role
from app.restx import cors_header
from app.restx import jwt_parser
from app.restx import register_models_role
from app.schemas import RoleSchema
from app.services.db import delete_model
from app.services.db import insert_model
from app.services.db import model_get
from app.services.db import model_list_paginated
from app.services.db import patch_model
from app.services.rbac import role_required


role = Namespace('roles', 'API for accounting endpoints.' )

register_models_role(role)

@role.route('/<int:id>')
@role.expect(jwt_parser(role))
class ItemAPI(Resource):
    """Class base view для экземпляров ролей."""
    init_every_request = False
    # Ручки доступны только пользователям с ролью admin.
    decorators = [role_required(['admin']), jwt_required(refresh=True)]
    model = Role

    def _get_item(self, id):
        m = model_get(id, self.model)
        if m is None:
            abort(HTTPStatus.NOT_FOUND)
        return m

    @role.doc(responses={HTTPStatus.OK.value: 'Success'}, model=role.models['Role'])
    def get(self, id):
        item = self._get_item(id)
        return RoleSchema().dump(item)

    @role.expect(role.models['Role'])
    @role.doc(responses={HTTPStatus.NO_CONTENT.value: 'Success'})
    def patch(self, id):
        # Используем marshmallow_sqlalchemy, для удобства перевода в json,
        item = RoleSchema().load(request.json, transient=True)
        item.id = id
        patch_model(RoleSchema(load_instance=False).dump(item), self.model)
        return {'msg': 'Role updated!'}, HTTPStatus.NO_CONTENT

    @role.doc(responses={HTTPStatus.NO_CONTENT.value: 'Success'})
    def delete(self, id):
        delete_model(id, self.model)
        return {'msg': 'Role deleted!'}, HTTPStatus.NO_CONTENT


@role.route('/')
@role.doc(parser=jwt_parser(role))
class GroupAPI(Resource):
    """Ручка, для создания и получения списка ролей."""
    init_every_request = False
    decorators = [role_required(['admin']), jwt_required(refresh=True)]
    model = Role

    @role.doc(responses={HTTPStatus.OK.value: 'Success'}, model=[role.models['Role']])
    def get(self):
        # Используем пагинацию flask_sqlalchemy
        page = int(request.args.to_dict().get('page', 1))
        model_list = model_list_paginated(self.model, page)
        items = RoleSchema(load_instance=False).dump(model_list.items, many=True)
        return items, HTTPStatus.OK

    @role.doc(parser=cors_header(role), body=role.models['RoleNew'])
    @role.doc(responses={HTTPStatus.CREATED.value: 'Success'})
    def post(self):
        item = RoleSchema().load(request.json, transient=True)
        insert_model(RoleSchema(load_instance=False).dump(item), self.model)
        return {'msg': 'Role inserted!'}, HTTPStatus.CREATED
