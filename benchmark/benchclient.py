import operator
import os.path
import pickle
import asyncio
from itertools import accumulate
from time import time

import numpy as np
import pandas as pd
from datasets import load_from_disk
from tqdm.asyncio import tqdm

from db.db import AsyncDB
from db.async_operations import query_db, add_items
from db.models import Item, item_to_qid_array

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
        return np.nan, np.nan

async def send_request(idx: int, db: AsyncDB):
    try:
        start = time()
        answer = await query_db(trace_ds[idx]['query_embeddings'], db.SessionLocal)
        vec_array = item_to_qid_array(answer)
        return start, time(), vec_array, trace_ds[idx]['query_id']
    except Exception:
        return np.nan, np.nan, np.nan, np.nan

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

async def execute_benchmark(async_db, indexing_method, run_number, requests_per_second):
    print("Starting benchmark...")

    trace = pickle.load(open(os.path.join(current_dir, 'trace/trace.pkl'), 'rb'))

    user = User(async_db)
    start = time()

    tasks = []
    arrivals = make_arrivals(len(trace[:200]), requests_per_second)
    for t, arrival in zip(trace[:200], arrivals):
        type, idx = t[0], t[1]
        tasks.append(asyncio.create_task(user.run(idx, type, arrival, start)))

    results = await tqdm.gather(*tasks)

    item_log, query_log = [], []
    for r, t in results:
        if t == 'insert':
            item_log.append(r)
        elif t == 'query':
            query_log.append(r)


    item_df = pd.DataFrame(item_log, columns=['start_time', 'end_time'])
    query_df = pd.DataFrame(query_log, columns=['start_time', 'end_time', 'qid_array', 'query_id'])
    item_df.to_pickle(os.path.join(results_dir, f'item_log_{indexing_method}_req{requests_per_second}_{run_number}.pkl'))
    query_df.to_pickle(os.path.join(results_dir, f'query_log_{indexing_method}_req{requests_per_second}_{run_number}.pkl'))
