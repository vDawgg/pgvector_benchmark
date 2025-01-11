import os.path
import pickle
import asyncio
from time import time
from multiprocessing.pool import Pool

from datasets import load_from_disk

from db.db import DB
from db.operations import query_db, add_items
from models.models import Item

# TODO: Set trace dir somewhere centrally
current_dir = os.path.dirname(os.path.realpath(__file__))
results_dir = os.path.join(current_dir, "results")
trace_ds = load_from_disk(os.path.join(current_dir, 'trace/trace.hf'))

class User:
    def __init__(self, _db, max_queries):
        self.db = _db
        self.cur_queries = 0
        self.max_queries = max_queries

    def increment_cur_queries(self):
        self.cur_queries += 1
        if self.cur_queries == self.max_queries:
            self.db.teardown()


async def save_items(idx: int, db: DB):
    start = time()
    items = []
    for i in range(10):
        items.append(
            Item(
                q_id=trace_ds[idx]['query_id'],
                text=trace_ds[idx]['passages'][i],
                vec=trace_ds[idx]['passage_embeddings'][i],
            )
        )
    add_items(items, db.SessionLocal)
    return start, time()

async def send_request(idx: int, db: DB):
    start = time()
    answer = query_db(trace_ds[idx]['query_embeddings'], db.SessionLocal)
    return start, time(), answer

async def run_user(trace, db: DB):
    inserts = []
    queries = []
    for type, idx, arrival in trace:
        if type == "insert":
            inserts.append(await save_items(idx, db))
        else:
            queries.append(await send_request(idx, db))

    return inserts, queries

async def run_users(trace):
    num_users = 10

    steps = int(len(trace)/num_users)
    steps = 1 if steps == 0 else steps
    tasks = []
    for i in range(0, len(trace), steps):
        tasks.append(asyncio.create_task(run_user(trace[i:i+steps], DB(db_url))))

    results = await asyncio.gather(*tasks)

    inserts, queries = [], []
    for i, q in results:
        inserts.extend(i)
        queries.extend(q)

    return inserts, queries

def start_coroutine(trace):
    inserts, queries = asyncio.run(run_users(trace))
    return inserts, queries

def make_batch_for_cpu_cores(lst, num_cores):
    batch_size = len(lst) // num_cores
    return [lst[i:i+batch_size] for i in range(0, len(lst), batch_size)]

def execute_benchmark(pg_url: str):
    global db_url
    db_url = pg_url

    print("Starting benchmark...")

    trace = pickle.load(open(os.path.join(current_dir, 'trace/trace.pkl'), 'rb'))
    chunks = make_batch_for_cpu_cores(trace, os.cpu_count())

    pool = Pool()
    results = pool.imap(start_coroutine, chunks)

    item_log, query_log = [], []
    for i, q in results:
        item_log.extend(i)
        query_log.extend(q)

    pickle.dump(item_log, open(os.path.join(results_dir, 'item_log.pkl'), 'wb'))
    pickle.dump(query_log, open(os.path.join(results_dir, 'query_log.pkl'), 'wb'))
