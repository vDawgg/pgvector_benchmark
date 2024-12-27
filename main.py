from utils.fill_db import fill_db
from db.operations import is_empty
from benchmark.benchclient import execute_benchmark

if __name__ == '__main__':
    if is_empty():
        fill_db()
    execute_benchmark()
    print('DONE')