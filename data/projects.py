import sqlalchemy as sql
from data.db_session import SQL_BASE
from sqlalchemy import orm

from sqlalchemy_serializer import SerializerMixin


class Project(SQL_BASE, SerializerMixin):
    __tablename__ = "projects"

    id = sql.Column(sql.Integer, primary_key=True, autoincrement=True)
    title = sql.Column(sql.String, nullable=False)
    idea = sql.Column(sql.String, nullable=False)
    presentation = sql.Column(sql.String, nullable=False)  # TODO: оценки проекта
    user_id = sql.Column(sql.Integer, sql.ForeignKey("users.id"))
    user = orm.relation("User")