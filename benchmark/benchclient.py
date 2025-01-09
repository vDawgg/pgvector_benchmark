import os.path
import pickle
import asyncio
import random
from time import time
from typing import List

from datasets import load_from_disk
from tqdm import tqdm

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

async def execute_benchmark(pg_url: str):
    print("Starting benchmark...")
    start = time()

    trace = pickle.load(open(os.path.join(current_dir, 'trace/trace.pkl'), 'rb'))

    users: List[User] = [User(pg_url, random.randint(1, 10)) for _ in range(10)]
    num_users = []
    inserts = []
    queries = []
    for type, idx, arrival in tqdm(trace):
        filter(lambda u: u.curr_queries >= u.max_queries, users)

        if random.random() > 0.5:
            users.append(User(DB(pg_url), random.randint(1, 10)))

        cur_user = random.choice(users)

        await asyncio.sleep(max(0, arrival - (time() - start)))

        if type == "insert":
            inserts.append(asyncio.create_task(save_items(idx, cur_user.db)))
        else:
            queries.append(asyncio.create_task(send_request(idx, cur_user.db)))
        num_users.append(len(users))

        cur_user.increment_cur_queries()

    item_log = await asyncio.gather(*inserts)
    query_log = await asyncio.gather(*queries)

    pickle.dump(num_users, open(os.path.join(current_dir, 'results/num_users.pkl'), 'wb'))
    pickle.dump(item_log, open(os.path.join(results_dir, 'item_log.pkl'), 'wb'))
    pickle.dump(query_log, open(os.path.join(results_dir, 'query_log.pkl'), 'wb'))