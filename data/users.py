import sqlalchemy as sql
from sqlalchemy import orm

from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin

from data.db_session import SQL_BASE

from werkzeug.security import check_password_hash, generate_password_hash


class User(SQL_BASE, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sql.Column(sql.Integer, primary_key=True, autoincrement=True)
    login = sql.Column(sql.String, nullable=False)
    surname = sql.Column(sql.String, nullable=False)
    name = sql.Column(sql.String, nullable=False)
    patronymic = sql.Column(sql.String, nullable=True)
    grade = sql.Column(sql.String, nullable=False)
    password = sql.Column(sql.String, nullable=True)
    access_level = sql.Column(sql.Integer, nullable=False)
    projects = orm.relation("Project", back_populates="user")

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)