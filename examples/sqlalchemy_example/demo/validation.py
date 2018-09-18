import hug
from marshmallow import fields
from marshmallow.decorators import validates_schema
from marshmallow.schema import Schema
from marshmallow_sqlalchemy import ModelSchema

from demo.context import SqlalchemyContext
from demo.models import TestUser, TestModel


@hug.type(extend=hug.types.text, chain=True, accept_context=True)
def unique_username(value, context: SqlalchemyContext):
    if context.db.query(
        context.db.query(TestUser).filter(
            TestUser.username == value
        ).exists()
    ).scalar():
        raise ValueError('User with a username {0} already exists.'.format(value))
    return value


class CreateUserSchema(Schema):
    username = fields.String()
    password = fields.String()

    @validates_schema
    def check_unique_username(self, data):
        if self.context.db.query(
            self.context.db.query(TestUser).filter(
                    TestUser.username == data['username']
            ).exists()
        ).scalar():
            raise ValueError('User with a username {0} already exists.'.format(data['username']))


class DumpUserSchema(ModelSchema):

    @property
    def session(self):
        return self.context.db

    class Meta:
        model = TestModel
        fields = ('name',)


class DumpSchema(Schema):
    users = fields.Nested(DumpUserSchema, many=True)
