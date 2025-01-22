import asyncio
from argparse import ArgumentParser

from db.db import DB, AsyncDB
from models.models import init_mappings
from db.utils import fill_db, add_index
from db.operations import is_empty
from benchmark.benchclient import execute_benchmark


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("--db_host", help="Host of database (e.g. localhost)", default="localhost")
    parser.add_argument("--indexing_method", help="Indexing method", default="", choices=["ivfflat", "hnsw"])
    parser.add_argument("--requests_per_second", help="Average number of requests per second", default=5)
    parser.add_argument("--run_number", help="Run number", default=0, type=int)
    args = parser.parse_args()
    args = vars(args)

    db_host = args.pop("db_host")
    pg_url = f"postgresql+psycopg://postgres:123@{db_host}"
    indexing_method = args.pop("indexing_method")
    request_per_second = args.pop("requests_per_second")
    run_number = args.pop("run_number")

    db = DB(pg_url)
    db.ensure_pgvector()
    init_mappings(db.engine)
    if is_empty(db.SessionLocal):
        fill_db(pg_url)
    add_index(db, indexing_method)
    db.teardown()

    async_db = AsyncDB(pg_url)
    asyncio.run(execute_benchmark(async_db, indexing_method, run_number, request_per_second))

    print('DONE')