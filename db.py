import atexit
import datetime
import os
from dotenv import load_dotenv

from sqlalchemy import DateTime, Integer, String, func, Boolean, ForeignKey
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import (DeclarativeBase, MappedColumn, mapped_column,
                            sessionmaker)

from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER", "app")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "secret")
POSTGRES_DB = os.getenv("POSTGRES_DB", "app")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "127.0.0.1")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5431")

POSTGRES_DSN = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
    f"{POSTGRES_HOST}:{POSTGRES_PORT}/"
    f"{POSTGRES_DB}"
)

engine = create_engine(POSTGRES_DSN)
atexit.register(engine.dispose)
Session = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class Ads(Base):
    __tablename__ = "ads"

    id: MappedColumn[int] = mapped_column(Integer, primary_key=True)
    title: MappedColumn[str] = mapped_column(String(100), nullable=False)
    description: MappedColumn[str] = mapped_column(String(1000), nullable=True)
    created_at: MappedColumn[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    owner_id: MappedColumn[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    @property
    def id_dict(self):
        return {"id": self.id}

    @property
    def dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "created_at": int(self.created_at.timestamp()),
            "owner": self.owner_id,
        }

class User(Base):
    __tablename__ = "users"

    id: MappedColumn[int] = mapped_column(Integer, primary_key=True)
    username: MappedColumn[str] = mapped_column(String(100),unique=True, nullable=False)
    email: MappedColumn[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: MappedColumn[str] = mapped_column(String(255), nullable=False)

    def hash_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)


# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)