import os.path
import pickle
import asyncio
from time import time

from datasets import load_from_disk
from tqdm import tqdm

from db.db import DB
from db.operations import query_db, add_items
from models.models import Item

# TODO: Set trace dir somewhere centrally
current_dir = os.path.dirname(os.path.realpath(__file__))
results_dir = os.path.join(current_dir, "results")
trace_ds = load_from_disk(os.path.join(current_dir, 'trace/trace.hf'))

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

class User:
    def __init__(self, _db):
        self.db = _db
        self.cur_queries = 0

    async def run(self, idx, request_type, arrival, start):
        if request_type == 'query':
            return await send_request(idx, self.db)
        else:
            return await send_request(idx, self.db)

async def execute_benchmark(pg_url: str):
    global db_url
    db_url = pg_url

    print("Starting benchmark...")

    trace = pickle.load(open(os.path.join(current_dir, 'trace/trace.pkl'), 'rb'))

    num_users = 200
    users = [User(DB(db_url)) for _ in range(num_users)]

    tasks = []
    start = time()
    for type, idx, arrival in tqdm(trace):
        await asyncio.sleep(max(0, arrival - (time() - start)))
        user = users.pop(0)
        tasks.append(asyncio.create_task(user.run(idx, type, arrival, start)))
        users.append(user)

    results = await asyncio.gather(*tasks)

    item_log, query_log = [], []
    for r in results:
        if len(r) == 2:
            item_log.append(r)
        else:
            query_log.append(r)

    pickle.dump(item_log, open(os.path.join(results_dir, 'item_log.pkl'), 'wb'))
    pickle.dump(query_log, open(os.path.join(results_dir, 'query_log.pkl'), 'wb'))
