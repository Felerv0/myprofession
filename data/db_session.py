import sqlalchemy as sql
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec

SQL_BASE = dec.declarative_base()

__factory = None


def global_init(db_file):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("No database file")

    con = f"sqlite:///{db_file.strip()}?check_same_thread=False"
    print(f"Connecting to {con}")

    engine = sql.create_engine(con, echo=True)
    __factory = orm.sessionmaker(bind=engine)

    from data import __all_models

    SQL_BASE.metadata.create_all(engine)


def create_session():
    global __factory
    return __factory()