from sqlalchemy import create_engine, text, NullPool, Engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncEngine

Base = declarative_base()

class AsyncDB:
    def __init__(self, pg_url):
        self.pg_url = pg_url
        self.engine: AsyncEngine = create_async_engine(
            self.pg_url,
            poolclass=NullPool,
        )
        self.SessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
        )

    def new_session(self) -> None:
        self.SessionLocal = async_sessionmaker(bind=self.engine)

    def teardown(self) -> None:
        self.engine.dispose()

class DB:
    def __init__(self, pg_url):
        self.engine: Engine = create_engine(pg_url, poolclass=NullPool, connect_args={'connect_timeout': 10})
        self.SessionLocal: sessionmaker[Session] = sessionmaker(bind=self.engine)

    def ensure_pgvector(self):
        with self.SessionLocal() as session:
            session.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            session.commit()

    def teardown(self) -> None:
        self.engine.dispose()
