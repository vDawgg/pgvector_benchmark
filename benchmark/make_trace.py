import pickle
import random
import os
from typing import List
import itertools

from datasets import load_from_disk


def generate_random_arrivals(rate: float, count: int) -> List[float]:
    """
    Generate 'count' arrival times from a Poisson process with average rate 'rate'.
    Return a sorted list of arrival times.
    """
    arrivals = []
    current_time = 0.0
    for _ in range(count):
        # Exponential inter-arrival time
        inter_arrival = random.uniform(0, rate)
        current_time += inter_arrival
        arrivals.append(current_time)
    return arrivals

def make_trace():
    test_ds = load_from_disk(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "../data/dataset/test_dataset.hf")
    )
    test_ds.save_to_disk(os.path.join("./trace/trace.hf"))

    insert_idx = [("insert", i) for i in range(10000, len(test_ds))]
    query_idx = [("query", random.randint(0, 10000 + i - 1)) for i in range(len(test_ds))]
    arrivals = generate_random_arrivals(.01, len(test_ds) - 10000)

    combined = [x for x in itertools.chain.from_iterable(itertools.zip_longest(insert_idx, query_idx)) if x]

    trace = [(*c, a) for c, a in zip(combined, arrivals)]

    with open('./trace/trace.pkl', 'wb') as trace_f:
        pickle.dump(trace, trace_f)

if __name__ == "__main__":
    make_trace()