from sentence_transformers import SentenceTransformer
from datasets import load_dataset


model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2', device="cuda:0")


def make_embeddings(batch):
    passage_texts = [text for d in batch["passages"] for text in d["passage_text"]]
    passage_embeddings = model.encode(passage_texts)
    query_embeddings = model.encode(batch["query"])
    passage_embeddings = [passage_embeddings[i:i+10] for i in range(0, len(passage_embeddings), 10)]

    return {
        "query_id": batch["query_id"],
        "passages": [d["passage_text"] for d in batch["passages"]],
        "passage_embeddings": passage_embeddings,
        "query": batch["query"],
        "query_embeddings": query_embeddings,
    }

def load_ds_with_embeddings():
    load_dataset("./dataset/train_dataset.hf")

if __name__ == "__main__":
    test_ds = load_dataset("microsoft/ms_marco", "v2.1", split="test")
    train_ds = load_dataset("microsoft/ms_marco", "v2.1", split="train")

    # Filter out passages with num texts != 10 to remove bias from ds
    test_ds = test_ds.filter(lambda x: len(x["passages"]["passage_text"]) == 10)
    train_ds = train_ds.filter(lambda x: len(x["passages"]["passage_text"]) == 10)

    print("> Making embeddings for test set")
    test_ds_embeddings = test_ds.map(make_embeddings, batched=True)
    test_ds_embeddings.save_to_disk("./dataset/test_dataset.hf")

    print("> Making embeddings for train set")
    train_ds.map(make_embeddings, batched=True).save_to_disk("./dataset/train_dataset.hf")