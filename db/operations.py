from sqlalchemy import Index
from sqlalchemy.orm import sessionmaker, Session
from tqdm import tqdm
from pgvector.psycopg import register_vector
import psycopg

from db.models import *


# Bulk insert using psycopg for faster setup
def bulk_insert(items: [Item], pg_url: str) -> None:
    print(f"> Inserting {len(items)} items in bulk...")
    with psycopg.connect(f'postgresql://{pg_url.split("//")[1]}:5432/postgres') as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            with cur.copy("COPY vecdatatable (q_id, vec) FROM STDIN WITH (FORMAT BINARY)") as copy:
                copy.set_types(['integer', 'vector'])
                for item in tqdm(items):
                    copy.write_row([item.q_id, item.vec])
        conn.commit()


def is_empty(session_local: sessionmaker[Session]) -> int:
    with session_local() as session:
        return session.query(Item).count() == 0


def add_hnsw(engine: Engine) -> None:
    Index(
        'my_index',
        Item.vec,
        postgresql_using='hnsw',
        postgresql_with={'m': 10, 'ef_construction': 20}, # This can be chosen rather arbitrarily, might still be interesting to tune
        postgresql_ops={'vec': 'vector_l2_ops'}
    ).create(engine)


def add_ivfflat(engine: Engine) -> None:
    Index(
        'my_index',
        Item.vec,
        postgresql_using='ivfflat',
        postgresql_with={'lists': 100}, # This is recommended for DS smaller than 1 MIO rows (lists=rows/1000), probes should be sqrt(lists)
        postgresql_ops={'vec': 'vector_l2_ops'}
    ).create(engine)
