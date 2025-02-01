from tqdm import tqdm

from db.models import Item
from db.db import DB
from db.operations import add_hnsw, add_ivfflat, bulk_insert
from datasets import load_from_disk

def make_init_set():
    ds = load_from_disk('./benchmark/trace/trace.hf')  # TODO: Parameterize this properly

    items = []
    for item in tqdm(ds.select(range(10000))): # TODO: Parameterize this ideally
        for i in range(len(item["passages"])):
            items.append(
                Item(
                    q_id=item["query_id"],
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

def add_index(db: DB, indexing_method: str):
    if indexing_method == 'ivfflat':
        add_ivfflat(db.engine)
    elif indexing_method == 'hnsw':
        add_hnsw(db.engine)
