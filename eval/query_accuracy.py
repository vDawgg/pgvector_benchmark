import os

import pandas as pd
from datasets import load_from_disk


def recall_at_r(query_log, ds):
    q_ids = query_log['query_id']
    items = query_log['qid_array']

    recall_list = []
    for q_id, item in zip(q_ids, items):
        relevant_items = sum([1 for i in item if i == q_id])
        recall = relevant_items / len(items)
        recall_list.append(recall)

    return recall_list, sum(recall_list) / len(recall_list)


def load_data(run, indexing_method, requests_per_sec):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    benchmark_dir = os.path.join(current_dir, "../benchmark")
    results_dir = os.path.join(benchmark_dir, "results")
    trace_dir = os.path.join(benchmark_dir, "trace")
    trace_ds = load_from_disk(os.path.join(trace_dir, 'trace.hf'))
    query_log = pd.read_pickle(os.path.join(results_dir, f'query_log_{indexing_method}_req{requests_per_sec}_{run}.pkl'))
    return trace_ds, query_log


if __name__ == '__main__':
    trace_ds, query_log = load_data(1000, '', 5)
    recall_list, avg_recall = recall_at_r(query_log, trace_ds)
    print(avg_recall)
