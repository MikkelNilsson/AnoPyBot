from sqlalchemy import create_engine
from sqlalchemy.orm import Session as sql_session, sessionmaker

from models import Server


Session = sessionmaker()


def setup_database(connection_string):
    engine = create_engine(connection_string)
    Session.configure(bind=engine)


def _get_server_data(db: sql_session, server_id: int) -> Server:
    res = db.query(Server).filter(Server.server_id == server_id).first()
    return res

def get_server_data(server_id: int) -> Server:
    with Session() as db:
        return _get_server_data(db, server_id)

def get_command_prefix_or_initiate(server_id):
    with Session() as db:
        server = _get_server_data(db, server_id)
        if not server:
            server = Server(server_id=server_id)
            db.add(server)
            db.commit()
        return str(server.prefix)


def update_prefix(server_id: int, prefix: str):
    with Session() as db:
        db.query(Server).filter(Server.server_id == server_id).update(
            {"prefix": prefix}
        )
        db.commit()


def update_default_role(server_id: int, role: int):
    with Session() as db:
        server_data = _get_server_data(db, server_id)
        server_data.default_role = role
        db.commit()


def update_welcome_message(server_id: int, channel: int, message: str):
    with Session() as db:
        server_data = _get_server_data(db, server_id)
        server_data.welcome_channel = channel
        server_data.welcome_message = message
        db.commit()
