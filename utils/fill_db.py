from tqdm import tqdm

from models.models import Item
from db.operations import bulk_insert
from datasets import load_from_disk

def make_init_set():
    ds = load_from_disk('./benchmark/trace/trace.hf')  # TODO: Parameterize this properly

    items = []
    for item in tqdm(ds.select(range(10000))): # TODO: This needs to be a lot smaller or the other machine much larger
        for i in range(len(item["passages"])):
            items.append(
                Item(
                    q_id=item["query_id"],
                    text=item["passages"][i],
                    vec=item["passage_embeddings"][i]
                )
            )
    return items

def fill_db(pg_url: str):
    print('Making initial set')
    init_set = make_init_set()
    print('Inserting initial set into db')
    bulk_insert(init_set, pg_url)
    print('Done inserting initial set')