from models import User
import graphene
from graphql import GraphQLError
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from db import db


class UserObject(SQLAlchemyObjectType):
   class Meta:
       model = User
       interfaces = (graphene.relay.Node, )
       exclude_fields = ('password_hash')


class Viewer(graphene.ObjectType):
    class Meta:
        interfaces = (graphene.relay.Node, )

    all_users = SQLAlchemyConnectionField(UserObject)


class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()
    viewer = graphene.Field(Viewer)

    @staticmethod
    def resolve_viewer(root, info):
        auth_resp = User.decode_auth_token(info.context)
        if not isinstance(auth_resp, str):
            return Viewer()
        raise GraphQLError(auth_resp)


class SignUp(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
    user = graphene.Field(lambda: UserObject)
    auth_token = graphene.String()
    def mutate(self, info, **kwargs):
        user = User(username=kwargs.get('username'))
        user.set_password(kwargs.get('password'))
        db.session.add(user)
        db.session.commit()
        return SignUp(user=user, auth_token=user.encode_auth_token(user.uuid).decode())


class Login(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
    user = graphene.Field(lambda: UserObject)
    auth_token = graphene.String()

    def mutate(self, info, **kwargs):
        user = User.query.filter_by(username=kwargs.get('username')).first()
        if user is None or not user.check_password(kwargs.get('password')):
            raise GraphQLError("Invalid Credentials")
        return Login(user=user, auth_token=user.encode_auth_token(user.uuid).decode())


class Mutation(graphene.ObjectType):
    signup = SignUp.Field()
    login = Login.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)