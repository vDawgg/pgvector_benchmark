import asyncio
from argparse import ArgumentParser

from db.db import DB
from models.models import init_mappings
from db.utils import fill_db, add_index
from db.operations import is_empty
from benchmark.benchclient import execute_benchmark


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("--db_host", help="Host of database (e.g. localhost)", default="localhost")
    parser.add_argument("--indexing_method", help="Indexing method", default="", choices=["ivfflat", "hnsw"])
    args = parser.parse_args()
    args = vars(args)

    db_host = args.pop("db_host")
    pg_url = f"postgresql+psycopg://postgres:123@{db_host}"
    indexing_method = args.pop("indexing_method")

    db = DB(pg_url)
    db.ensure_pgvector()
    init_mappings(db.engine)
    if is_empty(db.SessionLocal):
        fill_db(pg_url)
    add_index(db, indexing_method)

    asyncio.run(execute_benchmark(pg_url))

    print('DONE')