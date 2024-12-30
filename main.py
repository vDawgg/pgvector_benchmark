import sys

from db.db import DB
from models.models import init_mappings
from utils.fill_db import fill_db
from db.operations import is_empty
from benchmark.benchclient import execute_benchmark

if __name__ == '__main__':
    pg_url = f"postgresql+psycopg://postgres:123@{sys.argv[1]}" if len(sys.argv) > 1 else "postgresql+psycopg://postgres:123@localhost"
    db = DB(pg_url)
    init_mappings(db.engine)
    if is_empty(db.SessionLocal):
        fill_db(pg_url)
    execute_benchmark(db.pg_url)
    print('DONE')