from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

import redis

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_redis():
    try:
        yield redis_client
    finally:
        pass