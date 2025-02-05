import os
import math
from collections import defaultdict

import numpy as np
import pandas as pd

current_dir = os.path.dirname(__file__)
plots_dir = os.path.join(current_dir, "plots")
benchmark_dir = os.path.join(current_dir, '..', 'benchmark')
results_dir = os.path.join(benchmark_dir, 'results')
logs_dir = os.path.join(results_dir, 'logs')
utilizations_dir = os.path.join(results_dir, 'utilization')

def chunked_average(data, win_size):
    data = np.array(data, dtype=float)
    n = len(data) // win_size * win_size
    data = data[:n].reshape(-1, win_size)
    return np.nanmean(data, axis=1)

def get_throughput_and_err_rate(df, requests_per_second, bin_size):
    end = df['end_time']

    mean = 1 / requests_per_second
    last_time = 0

    end_times = []
    errors = []
    for e in end:
        if math.isnan(e):
            errors.append(last_time + mean)
            end_times.append(np.nan)
        else:
            errors.append(np.nan)
            end_times.append(e)
            last_time = e

    end_times, errors = np.array(end_times), np.array(errors)
    start_time, end_time = np.nanmin(end_times), np.nanmax(end_times)

    bin_edges = np.arange(start_time, end_time + bin_size, bin_size)
    t_counts, edges = np.histogram(end_times, bins=bin_edges)
    e_counts, edges = np.histogram(errors, bins=bin_edges)
    throughput = t_counts / bin_size
    errors = e_counts / bin_size

    return throughput, errors

def get_latency_and_err_rate(df, requests_per_second, bin_size):
    start = df['start_time']
    end = df['end_time']

    latencies = []
    errors = []
    for s, e in zip(start, end):
        if math.isnan(s):
            latencies.append(np.nan)
            errors.append(1)
        else:
            latencies.append(e - s)
            errors.append(0)

    latencies = chunked_average(latencies, bin_size)
    err_rate = chunked_average(errors, bin_size)

    return latencies, err_rate

def get_current_running_requests(df, win_size):
    events = defaultdict(int)

    for start, end in zip(df["start_time"], df["end_time"]):
        if not math.isnan(start) and not math.isnan(end):
            s = int(start)
            e = int(end)
            events[s] += 1
            events[e] -= 1

    all_times = sorted(events.keys())
    concurrency = 0
    counts = []

    for t in all_times:
        concurrency += events[t]
        counts.append(concurrency)

    return chunked_average(counts, win_size)

def get_avg_latency_and_total_errors(requests_per_second, request_type, indexing_method):
    latencies = []
    errors = []
    for f in os.listdir(logs_dir):
        if requests_per_second in f and request_type in f and indexing_method in f:
            df = pd.read_pickle(os.path.join(logs_dir, f))

            start = df['start_time']
            end = df['end_time']

            for s, e in zip(start, end):
                if math.isnan(s):
                    errors.append(1)
                else:
                    latencies.append(e - s)

    print("Num errs:", len(errors))
    print("Avg latency:", np.mean(np.array(latencies)))

if __name__ == "__main__":
    get_avg_latency_and_total_errors(
        "15",
        "query",
        "ivfflat"
    )
