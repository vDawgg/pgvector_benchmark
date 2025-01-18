import pickle
import random
import os
import itertools
from itertools import accumulate
import operator

from datasets import load_from_disk


def make_trace(requests_per_second: int):
    test_ds = load_from_disk(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "../data/dataset/test_dataset.hf")
    )
    test_ds.save_to_disk(os.path.join("./trace/trace.hf"))

    insert_idx = [("insert", i) for i in range(10000, len(test_ds))]
    query_idx = [("query", random.randint(0, 10000 + i - 1)) for i in range(len(test_ds))]

    mean = 1 / requests_per_second
    arrivals = list(
        accumulate(
            [mean for _ in range(len(test_ds)*2)],
            operator.add
        )
    )

    trace = [x for x in itertools.chain.from_iterable(itertools.zip_longest(insert_idx, query_idx)) if x]
    trace = [(*t, a) for t, a in zip(trace, arrivals)]

    with open('./trace/trace.pkl', 'wb') as trace_f:
        pickle.dump(trace, trace_f)

if __name__ == "__main__":
    make_trace(15)
