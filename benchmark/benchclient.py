import os.path
import pickle
from time import time
from typing import Tuple
from multiprocessing import Pool

from datasets import load_from_disk
from tqdm import tqdm

from db.db import DB
from db.operations import query_db, add_items
from models.models import Item

# TODO: Set trace dir somewhere centrally
current_dir = os.path.dirname(os.path.realpath(__file__))
results_dir = os.path.join(current_dir, "results")
trace_ds = load_from_disk(os.path.join(current_dir, 'trace/trace.hf'))

def save_items(idx: int):
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

def send_request(idx: int):
    start = time()
    answer = query_db(trace_ds[idx]['query_embeddings'], db.SessionLocal)
    return start, time(), answer

def execute_interaction(idx: Tuple[int, int]):
    item_log = save_items(idx[0])
    query_log = send_request(idx[1])
    return item_log, query_log

def init_process(pg_url: str) -> None:
    global db
    db = DB(pg_url)

def execute_benchmark(pg_url: str):
    print("Starting benchmark...")
    insert_idx = pickle.load(open(os.path.join(current_dir, 'trace/insert_trace.pkl'), 'rb'))
    query_idx = pickle.load(open(os.path.join(current_dir, 'trace/query_trace.pkl'), 'rb'))

    pool = Pool(os.cpu_count(), initializer=init_process, initargs=(pg_url,))
    item_log, query_log = zip(*tqdm(pool.imap(execute_interaction, zip(insert_idx, query_idx)), total=len(insert_idx)))
    pickle.dump(item_log, open(os.path.join(results_dir, 'item_log.pkl'), 'wb'))
    pickle.dump(query_log, open(os.path.join(results_dir, 'query_log.pkl'), 'wb'))