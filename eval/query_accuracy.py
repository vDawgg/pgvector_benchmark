import math
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# TODO: Think about adding non-retrieval here as well or EXPLICITLY mention it
def mean_reciprocal_rank(q_ids, items):
    ranks = []
    for q_id, item in zip(q_ids, items):
        if not math.isnan(q_id):
            ranks.append(
                np.where(item == q_id)[0][0] if q_id in item else 0
            )
    return sum(ranks) / len(ranks)

def recall_at_r(q_ids, items):
    recall_list = []
    for q_id, item in zip(q_ids, items):
        if not math.isnan(q_id):
            relevant_items = sum([1 for i in item if i == q_id])
            recall = relevant_items / len(items)
            recall_list.append(recall)

    return recall_list, sum(recall_list) / len(recall_list)


def load_data(indexing_method):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    benchmark_dir = os.path.join(current_dir, "../benchmark")
    results_dir = os.path.join(benchmark_dir, "results", "logs")

    q_ids = []
    items = []
    for f in os.listdir(results_dir):
        if indexing_method in f and "query" in f:
            query_log = pd.read_pickle(os.path.join(results_dir, f))
            q_ids.extend(query_log['query_id'])
            items.extend(query_log['qid_array'])
    return q_ids, items


if __name__ == '__main__':
    q_ids, items = load_data("none")
    hnsw_q_ids, hnsw_items = load_data("hnsw")
    ivfflat_q_ids, ivfflat_items = load_data('ivfflat')

    rr, avg_rr = recall_at_r(q_ids, items)
    rr_hnsw, avg_rr_hnsw = recall_at_r(hnsw_q_ids, hnsw_items)
    rr_ivfflat, avg_rr_ivfflat = recall_at_r(ivfflat_q_ids, ivfflat_items)

    mrr = mean_reciprocal_rank(q_ids, items)
    mrr_hnsw = mean_reciprocal_rank(hnsw_q_ids, hnsw_items)
    mrr_ivfflat = mean_reciprocal_rank(ivfflat_q_ids, ivfflat_items)

    plt.bar(["No indexing", "hnsw", "ivfflat"], [avg_rr, avg_rr_hnsw, avg_rr_ivfflat])
    plt.ylabel("Recall")
    plt.title("Recall@10")
    plt.show()

    plt.bar(["No indexing", "hnsw", "ivfflat"], [mrr, mrr_hnsw, mrr_ivfflat])
    plt.ylabel("MRR")
    plt.title("MRR@10")
    plt.show()
