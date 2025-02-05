import math
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

current_dir = os.path.dirname(os.path.realpath(__file__))
plots_dir = os.path.join(current_dir, "plots")
benchmark_dir = os.path.join(current_dir, "../benchmark")
results_dir = os.path.join(benchmark_dir, "results", "logs")

def mean_reciprocal_rank(q_ids, items):
    ranks = []
    for q_id, item in zip(q_ids, items):
        if not math.isnan(q_id):
            ranks.append(
                np.where(item == q_id)[0][0] if q_id in item else 0
            )
    return ranks, sum(ranks) / len(ranks)


def recall_at_r(q_ids, items):
    recall_list = []
    for q_id, item in zip(q_ids, items):
        if not math.isnan(q_id):
            relevant_items = sum([1 for i in item if i == q_id])
            recall = relevant_items / len(items)
            recall_list.append(recall)

    return recall_list, sum(recall_list) / len(recall_list)


def load_all_data(indexing_method):
    q_ids = []
    items = []
    for f in os.listdir(results_dir):
        if indexing_method in f and "query" in f:
            query_log = pd.read_pickle(os.path.join(results_dir, f))
            q_ids.extend(query_log['query_id'])
            items.extend(query_log['qid_array'])
    return q_ids, items

def load_data_rr(indexing_method, request_rate):
    q_ids = []
    items = []
    for f in os.listdir(results_dir):
        if indexing_method in f and "query" in f and str(request_rate) in f:
            query_log = pd.read_pickle(os.path.join(results_dir, f))
            q_ids.extend(query_log['query_id'])
            items.extend(query_log['qid_array'])
    return q_ids, items

def save_plots(request_rate):
    if request_rate == 0:
        q_ids, items = load_all_data("none")
        hnsw_q_ids, hnsw_items = load_all_data("hnsw")
        ivfflat_q_ids, ivfflat_items = load_all_data('ivfflat')
    else:
        q_ids, items = load_data_rr("none", request_rate)
        hnsw_q_ids, hnsw_items = load_data_rr("hnsw", request_rate)
        ivfflat_q_ids, ivfflat_items = load_data_rr("ivfflat", request_rate)

    r, avg_r = recall_at_r(q_ids, items)
    r_hnsw, avg_r_hnsw = recall_at_r(hnsw_q_ids, hnsw_items)
    r_ivfflat, avg_r_ivfflat = recall_at_r(ivfflat_q_ids, ivfflat_items)

    rr, mrr = mean_reciprocal_rank(q_ids, items)
    rr_hnsw, mrr_hnsw = mean_reciprocal_rank(hnsw_q_ids, hnsw_items)
    rr_ivfflat, mrr_ivfflat = mean_reciprocal_rank(ivfflat_q_ids, ivfflat_items)

    plt.bar(["No indexing", "hnsw", "ivfflat"], [avg_r, avg_r_hnsw, avg_r_ivfflat])
    plt.ylabel("Recall")
    if request_rate == 0:
        plt.title("Recall@10")
        plt.savefig(os.path.join(plots_dir, "recall_at_10.png"))
    else:
        plt.title(f"Recall@10 [{request_rate} req/sec]")
        plt.savefig(os.path.join(plots_dir, f"recall_at_10_req{request_rate}.png"))
    plt.close()

    plt.bar(["No indexing", "hnsw", "ivfflat"], [mrr, mrr_hnsw, mrr_ivfflat])
    plt.ylabel("MRR")
    if request_rate == 0:
        plt.title("MRR@10")
        plt.savefig(os.path.join(plots_dir, "mrr_at_10_all.png"))
    else:
        plt.title(f"MRR@10 [{request_rate} req/sec]")
        plt.savefig(os.path.join(plots_dir, f"mrr_at_10_req{request_rate}.png"))
    plt.close()

if __name__ == '__main__':
    # Query accuracy for all
    save_plots(0)
    # Query accuracy for 10 req/sec
    save_plots(10)
    # Query accuracy for 15 req/sec
    save_plots(15)
