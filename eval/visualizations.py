import math
import os

import matplotlib.pyplot as plt
import pandas as pd

from eval.utils import get_throughput_and_err_rate, get_latency_and_err_rate, get_current_running_requests

current_dir = os.path.dirname(__file__)
plots_dir = os.path.join(current_dir, "plots")
benchmark_dir = os.path.join(current_dir, '..', 'benchmark')
results_dir = os.path.join(benchmark_dir, 'results')
logs_dir = os.path.join(results_dir, 'logs')
utilizations_dir = os.path.join(results_dir, 'utilization')


def make_double_plot(data_1, data_2, labels, y_labels, x_label, title, file_name):
    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, sharex=True, figsize=(8, 6))
    ax1.plot(data_1, label=labels[0], color='blue')
    ax1.set_ylabel(y_labels[0])
    ax1.set_title(title)
    ax1.legend(loc='best')
    ax2.plot(data_2, label=labels[1], color='red')
    ax2.set_ylabel(y_labels[1])
    ax2.set_xlabel(x_label)
    ax2.legend(loc='best')
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, file_name))
    plt.close()

def make_single_plot(data, y_label, x_label, title, file_name):
    plt.figure(figsize=(8, 3))
    plt.plot(data)
    plt.ylabel(y_label)
    plt.xlabel(x_label)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, file_name))
    plt.close()

def make_overlying_plot(data, y_label, x_label, title, file_name):
    plt.figure(figsize=(12, 6))
    colors = ['blue', 'red', 'green', 'orange', 'purple']
    for d, c in zip(data, colors):
        plt.plot(d, color=c)
    plt.ylabel(y_label)
    plt.xlabel(x_label)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, file_name))
    plt.close()

def plot_latency(df, request_type, indexing_method, request_rate, run_number, win_size):
    latencies, _ = get_latency_and_err_rate(df, request_rate, win_size)

    if indexing_method == "none":
        title = f"Latency Over Time [No indexing, {request_type}, {request_rate} req/sec, Run #{run_number}]"
    else:
        title = f"Latency Over Time [{indexing_method}, {request_type}, {request_rate} req/sec, Run #{run_number}]"

    make_single_plot(
        latencies,
        "Latency (seconds)",
        f"Requests (x{win_size})",
        title,
        f'latency_{request_type}_{indexing_method}_req{request_rate}_{run_number}.png'
    )

def plot_latency_and_err_rate(df, request_type, indexing_method, request_rate, run_number, win_size):
    latencies, err_rate = get_latency_and_err_rate(df, request_rate, win_size)

    if indexing_method == "none":
        title = f"Latency and Error Rate Over Time [No indexing, {request_type}, {request_rate} req/sec, Run #{run_number}]"
    else:
        title = f"Latency and Error Rate Over Time [{indexing_method}, {request_type}, {request_rate} req/sec, Run #{run_number}]"

    make_double_plot(
        latencies,
        err_rate,
        ["Latency", "Error Rate"],
        ["Latency (seconds)", "Error Rate"],
        f'Requests (x{win_size})',
        title,
        f'latency_and_err_{request_type}_{indexing_method}_req{request_rate}_{run_number}.png'
    )

def get_latencies(start, end):
    latencies = []
    for s, e in zip(start, end):
        if not math.isnan(s):
            latencies.append(e - s)
    return latencies

def boxplot_latency(l_type: str, requests_per_sec: str):
    hnsw = []
    ivfflat = []
    none = []
    for f in os.listdir(logs_dir):
        print(f)
        df = pd.read_pickle(os.path.join(logs_dir, f))
        if l_type in f and "hnsw" in f and requests_per_sec in f:
            hnsw.extend(get_latencies(df["start_time"], df["end_time"]))
        elif l_type in f and "ivfflat" in f and requests_per_sec in f:
            ivfflat.extend(get_latencies(df["start_time"], df["end_time"]))
        elif l_type in f and "none" in f and requests_per_sec in f:
            none.extend(get_latencies(df["start_time"], df["end_time"]))

    print(len(hnsw))

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_ylabel('Latency (seconds)')
    ax.boxplot([none, hnsw, ivfflat], labels=["No indexing", "hnsw", "ivfflat"])
    if l_type == "item":
        plt.title("Latencies for CREATE")
    else:
        plt.title("Latencies for READ")
    plt.show()

def plot_throughput(df, request_type, indexing_method, requests_per_second, run_number, bin_size):
    throughput, _ = get_throughput_and_err_rate(df, requests_per_second, bin_size)
    if indexing_method == "none":
        title = f'Throughput Over Time (binned) [No indexing, {request_type}, {requests_per_second} req/sec, Run #{run_number}]'
    else:
        title = f'Throughput Over Time (binned) [{indexing_method}, {request_type}, {requests_per_second} req/sec, Run #{run_number}]'
    make_single_plot(
        throughput,
        "Throughput",
        "Time (minutes)",
        title,
        f'throughput_{request_type}_{indexing_method}_req{requests_per_second}_{run_number}.png'
    )

def plot_throughput_and_err_rate(df, request_type, indexing_method, requests_per_second, run_number, bin_size):
    throughput, error_rate = get_throughput_and_err_rate(df, requests_per_second, bin_size)
    if indexing_method == "none":
        title = f'Throughput and Error Rate Over Time (binned) [No indexing, {request_type}, {requests_per_second} req/sec, Run #{run_number}]'
    else:
        title = f'Throughput and Error Rate Over Time (binned) [{indexing_method}, {request_type}, {requests_per_second} req/sec, Run #{run_number}]'
    make_double_plot(
        throughput,
        error_rate,
        ["Throughput", "Error Rate"],
        ["Throughput (req/sec)", "Error Rate"],
        'Time (minutes)',
        title,
        f'throughput_and_err_{request_type}_{indexing_method}_req{requests_per_second}_{run_number}.png'
    )

def plot_current_running_requests(df, indexing_method, request_type, requests_per_sec, run_number, win_size):
    rr = get_current_running_requests(df, win_size)
    if indexing_method == "none":
        title = f"Number of in-flight requests over time [No indexing, {request_type}, {requests_per_sec} req/s, Run #{run_number}]"
    else:
        title = f"Number of in-flight requests over time [{indexing_method}, {request_type}, {requests_per_sec} req/s, Run #{run_number}]"
    make_single_plot(
        rr,
        "Number of in-flight requests",
        "Time (seconds)",
        title,
        f'in_flight_requests_{request_type}_{indexing_method}_req{requests_per_sec}_{run_number}.png'
    )

def plot_cpu_utilizations():
    for d in os.listdir(utilizations_dir):
        parts = d.split('_')
        requests_per_sec = parts[0].split('req')[1]
        indexing_method = parts[1]
        run_number = parts[2]
        sut_utilization = open(os.path.join(utilizations_dir, d, "cpu_sut.csv"), "r")
        client_utilization = open(os.path.join(utilizations_dir, d, "cpu_client.csv"), "r")
        cpu_sut = [float(line.split(",")[1].strip()) for line in sut_utilization.readlines()[5:]]
        cpu_client = [float(line.split(",")[1].strip()) for line in client_utilization.readlines()[5:]]
        fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, sharex=True, sharey=True, figsize=(8, 6))
        ax1.plot(cpu_sut, label='SUT', color='C0')
        ax1.set_ylabel('CPU Utilization')
        ax1.set_xlabel('Time')
        if indexing_method == "":
            ax1.set_title(f"CPU Utilization for SUT and Client (No indexing, {requests_per_sec} req/s, Run #{run_number})")
        else:
            ax1.set_title(f"CPU Utilization for SUT and Client ({indexing_method}, {requests_per_sec} req/s), Run #{run_number}")
        ax1.legend(loc='upper left')
        ax2.plot(cpu_client, label='Client', color='red')
        ax2.set_ylabel('CPU Utilization')
        ax2.set_xlabel('Time')
        ax2.legend(loc='upper left')
        plt.tight_layout()
        plt.savefig(os.path.join(plots_dir, f"cpu_utilization_{indexing_method}_req{requests_per_sec}_{run_number}.png"))
        plt.close()

def make_combined_plots():
    data = {}
    for f in os.listdir(logs_dir):
        parts = f.split('_')
        request_type = parts[0]
        indexing_method = parts[2]
        requests_per_sec = int(parts[3].split('req')[1])
        if indexing_method not in data:
            data[indexing_method] = {}
        if request_type not in data[indexing_method]:
            data[indexing_method][request_type] = {
                "throughput": {},
                "latency": {}
            }
        if requests_per_sec not in data[indexing_method][request_type]["throughput"]:
            data[indexing_method][request_type]["throughput"][requests_per_sec] = []
            data[indexing_method][request_type]["latency"][requests_per_sec] = []
        data[indexing_method][request_type]["throughput"][requests_per_sec].append(
            get_throughput_and_err_rate(
                pd.read_pickle(os.path.join(logs_dir, f)),
                requests_per_sec,
                60
            )[0]
        )
        data[indexing_method][request_type]["latency"][requests_per_sec].append(
            get_latency_and_err_rate(
                pd.read_pickle(os.path.join(logs_dir, f)),
                requests_per_sec,
                60
            )[0]
        )

    for im in data.keys():
        for rt in data[im].keys():
            make_overlying_plot(
                data[im][rt]["throughput"][10],
                "Throughput (req/sec)",
                "Time (minutes)",
                f"Throughput Over Time For All Runs [{im if im != 'none' else 'No indexing'}, {rt}, 10 req/sec]",
                f"throughput_all_{rt}_{im}_req10.png"
            )
            make_overlying_plot(
                data[im][rt]["throughput"][15],
                "Throughput (req/sec)",
                "Time (minutes)",
                f"Throughput Over Time For All Runs [{im if im != 'none' else 'No indexing'}, {rt}, 15 req/sec]",
                f"throughput_all_{rt}_{im}_req15.png"
            )
            make_overlying_plot(
                data[im][rt]["latency"][10],
                "Latency (seconds)",
                "Requests (x60)",
                f"Latency Over Time For All Runs [{im if im != 'none' else 'No indexing'}, {rt}, 10 req/sec]",
                f"latency_all_{rt}_{im}_req10.png"
            )
            make_overlying_plot(
                data[im][rt]["latency"][15],
                "Latency (seconds)",
                "Requests (x60)",
                f"Latency Over Time For All Runs [{im if im != 'none' else 'No indexing'}, {rt}, 15 req/sec]",
                f"latency_all_{rt}_{im}_req15.png"
            )

def make_plots_for_run(file_name, df):
    parts = file_name.split("_")
    request_type = 'CREATE' if parts[0] == 'item' else 'READ'
    indexing_method = parts[2]
    requests_per_sec = int(parts[3].split('req')[1])
    run_number = parts[4].split('.')[0]

    plot_latency_and_err_rate(df, request_type, indexing_method, requests_per_sec, run_number, 60)
    plot_throughput_and_err_rate(df, request_type, indexing_method, requests_per_sec, run_number, 60)

    plot_latency(df, request_type, indexing_method, requests_per_sec, run_number, 60)
    plot_throughput(df, request_type, indexing_method, requests_per_sec, run_number, 60)
    plot_current_running_requests(df, indexing_method, request_type, requests_per_sec, run_number, 60)

if __name__ == "__main__":
    for f in os.listdir(logs_dir):
        df = pd.read_pickle(os.path.join(logs_dir, f))
        make_plots_for_run(f, df)

    plot_cpu_utilizations()
    make_combined_plots()
