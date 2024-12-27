import os.path
import pickle
from time import time
from typing import Tuple
from multiprocessing import Pool

import torch
from tqdm import tqdm

from db.db import get_session
from db.operations import query_db, add_items
from models.models import Item

# TODO: Set trace dir somewhere centrally
current_dir = os.path.dirname(os.path.realpath(__file__))
results_dir = os.path.join(current_dir, "results")
trace_ds = torch.load(os.path.join(current_dir, 'trace/trace.pt'))

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
    add_items(items)
    return start, time()

def send_request(idx: int):
    start = time()
    answer = query_db(trace_ds[idx]['query_embeddings'])
    return start, time(), answer

def execute_interaction(idx: Tuple[int, int]):
    item_log = save_items(idx[0])
    query_log = send_request(idx[1])
    return item_log, query_log

def execute_benchmark():
    print("Starting benchmark...")
    insert_idx = pickle.load(open(os.path.join(current_dir, 'trace/insert_trace.pkl'), 'rb'))[:10000]
    query_idx = pickle.load(open(os.path.join(current_dir, 'trace/query_trace.pkl'), 'rb'))[:1000]

    pool = Pool(os.cpu_count()-4, initializer=get_session) # TODO: Change this value once deploying!
    item_log, query_log = zip(*tqdm(pool.imap(execute_interaction, zip(insert_idx, query_idx)), total=1000))
    pickle.dump(item_log, open(os.path.join(results_dir, 'item_log.pkl'), 'wb'))
    pickle.dump(query_log, open(os.path.join(results_dir, 'query_log.pkl'), 'wb'))