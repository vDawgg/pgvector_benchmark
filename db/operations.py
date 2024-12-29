from typing import Sequence

from sqlalchemy import select, Index, Engine
from sqlalchemy.orm import sessionmaker, Session
from tqdm import tqdm
from pgvector.psycopg import register_vector
import psycopg

from models.models import *


# Bulk insert using psycopg for faster setup
def bulk_insert(items: [Item], pg_url: str) -> None:
    print(f"> Inserting {len(items)} items in bulk...")
    with psycopg.connect(f'postgresql://{pg_url.split("//")[1]}:5432/postgres') as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            with cur.copy("COPY vecdatatable (q_id, text, vec) FROM STDIN WITH (FORMAT BINARY)") as copy:
                copy.set_types(['integer', 'text', 'vector'])
                for item in tqdm(items):
                    copy.write_row([item.q_id, item.text, item.vec])
        conn.commit()


def is_empty(SessionLocal: sessionmaker[Session]) -> int:
    with SessionLocal() as session:
        return session.query(Item).count() == 0


def add_item(item: Item, SessionLocal: sessionmaker[Session]) -> None:
    with SessionLocal() as session:
        session.add(item)
        session.commit()


def add_items(items: [Item], SessionLocal: sessionmaker[Session]) -> None:
    with SessionLocal() as session:
        session.add_all(items)
        session.commit()

def query_db(query: Item, SessionLocal: sessionmaker[Session], n=5) -> Sequence[Item]:
    with SessionLocal() as session:
        answer = (
            session
            .scalars(
                select(Item)
                .order_by(Item.vec.l2_distance(query))
                .limit(n)
            )
        )
        session.commit()
        return answer.all()


# TODO: Look into the config options being made here!
def add_hnsw(engine: Engine) -> None:
    Index(
        'my_index',
        Item.vec,
        postgresql_using='hnsw',
        postgresql_with={'m': 16, 'ef_construction': 64},
        postgresql_ops={'vec': 'vector_l2_ops'}
    ).create(engine)


# TODO: Look into the config options being made here!
def add_ivfflat(engine: Engine) -> None:
    Index(
        'my_index',
        Item.vec,
        postgresql_using='ivfflat',
        postgresql_with={'lists': 100},
        postgresql_ops={'vec': 'vector_l2_ops'}
    ).create(engine)