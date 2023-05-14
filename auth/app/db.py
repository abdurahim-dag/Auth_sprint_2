from contextlib import contextmanager
from typing import Generator
from typing import Optional

from redis import Redis
from sqlalchemy import Engine
from sqlalchemy.orm import Session


engine: Optional[Engine] = None
redis: Optional[Redis] = None

@contextmanager
def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def get_redis() -> Redis:
    return redis
