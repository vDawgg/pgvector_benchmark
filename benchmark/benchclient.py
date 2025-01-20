import operator
import os.path
import pickle
import asyncio
from collections import deque
from itertools import accumulate
from time import time

from datasets import load_from_disk
from tqdm.asyncio import tqdm

from db.db import AsyncDB
from db.async_operations import query_db, add_items
from models.models import Item


current_dir = os.path.dirname(os.path.realpath(__file__))
results_dir = os.path.join(current_dir, "results")
trace_ds = load_from_disk(os.path.join(current_dir, 'trace/trace.hf'))

def make_arrivals(num: int, mean: float):
    mean = 1 / mean
    return list(accumulate(
        [mean for _ in range(num)],
        operator.add
    ))

async def save_items(idx: int, db: AsyncDB):
    try:
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
        await add_items(items, db.SessionLocal)
        return start, time()
    except Exception as e:
        print(e)
        return None, None

async def send_request(idx: int, db: AsyncDB):
    try:
        start = time()
        answer = await query_db(trace_ds[idx]['query_embeddings'], db.SessionLocal)
        return start, time(), answer
    except Exception:
        return None, None, None

class User:
    def __init__(self, _db: AsyncDB):
        self.db = _db
        self.cur_queries = 0

    async def run(self, idx, request_type, arrival, start):
        await asyncio.sleep(max(0, arrival - (time() - start)))
        if request_type == 'query':
            return await send_request(idx, self.db), 'query'
        elif request_type == 'insert':
            return await save_items(idx, self.db), 'insert'

async def execute_benchmark(async_db):
    print("Starting benchmark...")

    trace = pickle.load(open(os.path.join(current_dir, 'trace/trace.pkl'), 'rb'))

    #users = deque([User(AsyncDB(db_url)) for _ in range(len(trace))])
    user = User(async_db)
    start = time()

    tasks = []
    arrivals = make_arrivals(len(trace), 10)
    for t, arrival in zip(trace, arrivals):
        type, idx = t[0], t[1]
        tasks.append(asyncio.create_task(user.run(idx, type, arrival, start)))

    results = await tqdm.gather(*tasks)

    item_log, query_log = [], []
    for r, t in results:
        if t == 'insert':
            item_log.append(r)
        elif t == 'query':
            query_log.append(r)

    pickle.dump(item_log, open(os.path.join(results_dir, 'item_log.pkl'), 'wb'))
    pickle.dump(query_log, open(os.path.join(results_dir, 'query_log.pkl'), 'wb'))
