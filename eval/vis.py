import math
import os
from collections import defaultdict

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def get_latencies_and_errors(start, end, win_size):
    latencies = []
    errors = []
    for s, e in zip(start, end):
        if math.isnan(s):
            latencies.append(np.nan)
            errors.append(1)
        else:
            latencies.append(e-s)
            errors.append(0)

    kernel = np.ones(win_size) / win_size
    err_rate = np.convolve(np.array(errors), kernel, 'same')

    return np.array(latencies), err_rate

def plot_latency(latencies, err_rate, request_type):
    range = np.arange(len(latencies))

    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, sharex=True, figsize=(8, 6))

    # Plot latency in the first (top) subplot
    ax1.plot(range, latencies, label='Latency', color='C0')
    ax1.set_ylabel('Latency (seconds)')
    ax1.set_title(f"Latency and Error Rate Over Time [{request_type}]")
    ax1.legend(loc='upper left')

    # Plot error rate in the second (bottom) subplot
    ax2.plot(range, err_rate, label='Error Rate', color='red')
    ax2.set_ylabel('Error Rate')
    ax2.set_xlabel('Request Index (or Time)')
    ax2.legend(loc='upper left')

    plt.tight_layout()
    plt.show()

def get_binned_throughput_and_errors(end, bin_size, rate):
    mean = 1 / rate
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
    bin_centers = (edges[:-1] + edges[1:]) / 2.0

    return bin_centers, throughput, errors

def plot_throughput(request_type, end, bin_size, rate):
    bin_centers, throughput, errors = get_binned_throughput_and_errors(end, bin_size, rate)

    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, sharex=True, figsize=(8, 6))
    ax1.plot(bin_centers, throughput, label='Throughput', color='C0')
    ax1.set_ylabel('Throughput (queries/min)')
    ax1.set_xlabel('Time (min)')
    ax1.set_title(f'Throughput and Error Rate Over Time (binned) [{request_type}]')
    ax1.legend(loc='upper left')

    ax2.plot(bin_centers, errors, label='Error Rate', color='red')
    ax2.set_ylabel('Error Rate (Errors/min)')
    ax2.set_xlabel('Time (min)')
    ax2.legend(loc='upper left')

    plt.tight_layout()
    plt.show()

def get_current_running_requests(df):
    events = defaultdict(int)

    for start, end in zip(df["start_time"], df["end_time"]):
        if not math.isnan(start) and not math.isnan(end):
            s = int(start)
            e = int(end)
            events[s] += 1
            events[e] -= 1

    all_times = sorted(events.keys())
    concurrency = 0
    times = []
    counts = []

    for t in all_times:
        concurrency += events[t]
        times.append(t)
        counts.append(concurrency)

    return times, counts

def plot_current_running_requests(insert_df, query_df):
    insert_range, insert_rr = get_current_running_requests(insert_df)
    query_range, query_rr = get_current_running_requests(query_df)

    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, sharex=True, figsize=(8, 6))

    ax1.plot(insert_range, insert_rr, label='CREATE', color='C0')
    ax1.set_ylabel('Num Requests')
    ax1.set_xlabel('Time (sec)')
    ax1.set_title("Number of in-flight requests over time")
    ax1.legend(loc='upper left')

    ax2.plot(query_range, query_rr, label='READ', color='red')
    ax2.set_ylabel('Num Requests')
    ax2.set_xlabel('Time (sec)')
    ax2.legend(loc='upper left')

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    indexing_method = "hnsw"
    requests_per_sec = 10
    run = 1

    results_dir = '../benchmark/results'

    insert_df = pd.read_pickle(os.path.join(results_dir, f'item_log_{indexing_method}_req{requests_per_sec}_{run}.pkl'))
    query_df = pd.read_pickle(os.path.join(results_dir, f'query_log_{indexing_method}_req{requests_per_sec}_{run}.pkl'))

    insert_start = insert_df['start_time']
    insert_end = insert_df['end_time']

    query_start = query_df['start_time']
    query_end = query_df['end_time']

    plot_latency(
        *get_latencies_and_errors(insert_start, insert_end, 100),
        'CREATE'
    )

    plot_latency(
        *get_latencies_and_errors(query_start, query_end, 100),
        'READ'
    )

    # TODO: Find out whether this bin size is sensible for the application
    plot_throughput('CREATE', insert_end, 60, requests_per_sec)

    plot_throughput('READ', query_end,60, requests_per_sec)

    plot_current_running_requests(insert_df, query_df)
