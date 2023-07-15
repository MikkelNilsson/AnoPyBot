from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from models import Server


Session = sessionmaker()


def setup_database(connection_string):
    engine = create_engine(connection_string)
    Session.configure(bind=engine)


def get_server_data(server_id, db: Session):
    res = db.query(Server).where(Server.server_id == server_id).first()
    return res


def get_command_prefix_or_initiate(server_id):
    with Session() as db:
        server = get_server_data(server_id, db)
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
