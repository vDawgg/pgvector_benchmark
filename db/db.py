from sqlalchemy import create_engine, text, NullPool
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session
import os

Base = declarative_base()

class DB:
    def __init__(self, pg_url):
        self.pg_url = pg_url
        self.SessionLocal = None
        self.engine = None
        self.get_session()
        with self.SessionLocal() as session:
            session.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            session.commit()

    def get_session(self):
        self.engine = create_engine(self.pg_url, poolclass=NullPool)  # . pool_pre_ping=True)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def teardown(self):
        self.engine.dispose()