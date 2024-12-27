from sqlalchemy import create_engine, text, NullPool
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session
import os


pg_url = "postgresql+psycopg://postgres:123@localhost"

SessionLocal = None
engine = None

def get_session():
    global SessionLocal
    global engine
    engine = create_engine(pg_url, poolclass=NullPool)  #. pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine)
    print("Engine created and SessionLocal set up in PID:", os.getpid())

get_session()

with SessionLocal() as session:
    session.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    session.commit()

Base = declarative_base()