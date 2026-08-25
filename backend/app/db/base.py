

import os
from functools import lru_cache

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Session,
    sessionmaker,
)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://pc_builder:pc_builder_password@localhost:5432/pc_builder",
)


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """Create (and cache) the SQLAlchemy engine on first call."""
    return create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)


def get_session_factory() -> sessionmaker[Session]:
    """Return a sessionmaker bound to the cached engine."""
    return sessionmaker(bind=get_engine(), class_=Session, expire_on_commit=False)


class Base(DeclarativeBase):
    

    pass


def get_db():
   
    session_factory = get_session_factory()
    db = session_factory()
    try:
        yield db
    finally:
        db.close()
