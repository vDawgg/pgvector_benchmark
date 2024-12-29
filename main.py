import sys

from db.db import DB
from models.models import init_mappings
from utils.fill_db import fill_db
from db.operations import is_empty
from benchmark.benchclient import execute_benchmark

if __name__ == '__main__':
    db = DB(sys.argv[1] if len(sys.argv) > 1 else "postgresql+psycopg://postgres:123@localhost")
    init_mappings(db.engine)
    if is_empty(db.SessionLocal):
        fill_db()
    execute_benchmark(db.pg_url)
    print('DONE')