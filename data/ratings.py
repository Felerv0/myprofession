import sqlalchemy as sql
from data.db_session import SQL_BASE
from sqlalchemy import orm


class Rating(SQL_BASE):
    __tablename__ = "ratings"

    id = sql.Column(sql.Integer, primary_key=True, autoincrement=True)
    project_id = sql.Column(sql.Integer, sql.ForeignKey("projects.id"), nullable=False)
    expert_id = sql.Column(sql.Integer, sql.ForeignKey("users.id"), nullable=False)
    story = sql.Column(sql.Integer, nullable=False)
    depth = sql.Column(sql.Integer, nullable=False)
    total = sql.Column(sql.Integer, nullable=False)

    project = orm.relation("Project")
    expert = orm.relation("User")