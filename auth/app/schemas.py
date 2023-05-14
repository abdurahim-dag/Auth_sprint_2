from app.ma import ma
from app.models import User, Role, UserSocial


class RoleSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = Role
        include_relationships = False
        load_instance = True


class UserSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = User
        include_relationships = False
        load_instance = True


class UserSocialSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = UserSocial
        include_relationships = True
        load_instance = True
