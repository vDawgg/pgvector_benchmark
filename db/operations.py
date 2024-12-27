from sqlalchemy import select, Index
from tqdm import tqdm
from pgvector.psycopg import register_vector
import psycopg

from db.db import SessionLocal, engine
from models.models import *


# Bulk insert using psycopg for faster setup
def bulk_insert(items: [Item]):
    print(f"> Inserting {len(items)} items in bulk...")

    # TODO: Set this somewhere centrally!
    with psycopg.connect("postgresql://postgres:123@localhost:5432/postgres") as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            with cur.copy("COPY vecdatatable (q_id, text, vec) FROM STDIN WITH (FORMAT BINARY)") as copy:
                copy.set_types(['integer', 'text', 'vector'])
                for item in tqdm(items):
                    copy.write_row([item.q_id, item.text, item.vec])
        conn.commit()


def is_empty():
    with SessionLocal() as session:
        return session.query(Item).count() == 0


def add_item(item: Item):
    with SessionLocal() as session:
        session.add(item)
        session.commit()


def add_items(items: [Item]):
    with SessionLocal() as session:
        session.add_all(items)
        session.commit()

def query_db(query: Item, n=5):
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
def add_hnsw():
    Index(
        'my_index',
        Item.vec,
        postgresql_using='hnsw',
        postgresql_with={'m': 16, 'ef_construction': 64},
        postgresql_ops={'vec': 'vector_l2_ops'}
    ).create(engine)


# TODO: Look into the config options being made here!
def add_ivfflat():
    Index(
        'my_index',
        Item.vec,
        postgresql_using='ivfflat',
        postgresql_with={'lists': 100},
        postgresql_ops={'vec': 'vector_l2_ops'}
    ).create(engine)