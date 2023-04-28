from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, BigInteger, String

Base = declarative_base()


class Server(Base):
    __tablename__ = "servers"
    server_id = Column(BigInteger, primary_key=True)
    prefix = Column(String(10), default="!")
    default_role = Column(BigInteger, default=0)
    welcome_channel = Column(BigInteger, default=0)
    welcome_message = Column(String(200), default="Welcome ¤name¤ to the server!")
    leave_channel = Column(BigInteger, default=0)
