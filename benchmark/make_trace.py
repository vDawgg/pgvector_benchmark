import pickle
import random
import os
import itertools

from datasets import load_from_disk


def make_trace():
    test_ds = load_from_disk(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "../data/dataset/test_dataset.hf")
    )
    test_ds = test_ds.select(range(55000))
    test_ds.save_to_disk(os.path.join("./trace/trace.hf"))

    insert_idx = [("insert", i) for i in range(10000, len(test_ds))]
    query_idx = [("query", random.randint(0, 10000 + i - 1)) for i in range(len(test_ds))]

    trace = [x for x in itertools.chain.from_iterable(itertools.zip_longest(insert_idx, query_idx)) if x]

    print(len(trace))

    with open('./trace/trace.pkl', 'wb') as trace_f:
        pickle.dump(trace, trace_f)

if __name__ == "__main__":
    make_trace()
