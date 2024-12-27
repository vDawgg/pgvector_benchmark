import pickle
import random
import os
from typing import List, Tuple

import torch.utils.data
from datasets import load_from_disk


def make_trace():
    test_ds = load_from_disk(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "../data/dataset/test_dataset.hf")
    )
    train_ds = load_from_disk(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "../data/dataset/train_dataset.hf")
    )
    train_ds.shuffle()
    trace_ds = torch.utils.data.ConcatDataset([test_ds, train_ds])
    torch.save(trace_ds, os.path.join("./trace/trace.pt"))

    insert_idx = range(len(test_ds), len(trace_ds))
    query_idx = [random.randint(0, len(test_ds) + i - 1) for i in range(len(train_ds))]

    with open('./trace/insert_trace.pkl', 'wb') as insert_f, open('./trace/query_trace.pkl', 'wb') as query_f:
        pickle.dump(insert_idx, insert_f)
        pickle.dump(query_idx, query_f)

if __name__ == "__main__":
    make_trace()