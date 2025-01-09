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


async def save_items(idx: int):
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

async def send_request(idx: int):
    start = time()
    answer = query_db(trace_ds[idx]['query_embeddings'], db.SessionLocal)
    return start, time(), answer

def init_process(pg_url: str) -> None:
    global db
    db = DB(pg_url)

async def execute_benchmark(pg_url: str):
    print("Starting benchmark...")
    start = time()

    trace = pickle.load(open(os.path.join(current_dir, 'trace/trace.pkl'), 'rb'))

    init_process(pg_url)

    inserts = []
    queries = []
    for type, idx, arrival in tqdm(trace):
        await asyncio.sleep(max(0, arrival - (time() - start)))

        if type == "insert":
            inserts.append(asyncio.create_task(save_items(idx)))
        else:
            queries.append(asyncio.create_task(send_request(idx)))

    item_log = await asyncio.gather(*inserts)
    query_log = await asyncio.gather(*queries)

    pickle.dump(item_log, open(os.path.join(results_dir, 'item_log.pkl'), 'wb'))
    pickle.dump(query_log, open(os.path.join(results_dir, 'query_log.pkl'), 'wb'))