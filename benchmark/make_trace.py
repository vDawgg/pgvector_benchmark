import pickle
import random
import os

from datasets import load_from_disk, concatenate_datasets


def make_trace():
    test_ds = load_from_disk(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "../data/dataset/test_dataset.hf")
    )
    train_ds = load_from_disk(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "../data/dataset/train_dataset.hf")
    )
    train_ds.shuffle()
    sharded_train_ds = train_ds.shard(2, 0)
    print(len(sharded_train_ds))
    trace_ds = concatenate_datasets([test_ds, sharded_train_ds])
    trace_ds.save_to_disk(os.path.join("./trace/trace.hf"))

    insert_idx = range(len(test_ds), len(trace_ds))
    query_idx = [random.randint(0, len(test_ds) + i - 1) for i in range(len(train_ds))]

    with open('./trace/insert_trace.pkl', 'wb') as insert_f, open('./trace/query_trace.pkl', 'wb') as query_f:
        pickle.dump(insert_idx, insert_f)
        pickle.dump(query_idx, query_f)

if __name__ == "__main__":
    make_trace()