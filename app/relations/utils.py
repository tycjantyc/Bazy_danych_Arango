import pandas as pd
import numpy as np
from tqdm import tqdm

def fetch_geometries(db, collection_name):
    """Fetch geometries from ArangoDB collection and convert to DataFrame."""
    collection = db.collection(collection_name)
    cursor = db.aql.execute(
        f'FOR doc IN {collection_name} RETURN {{id: doc._key, geometry: doc.geometry}}'
    )
    
    data = list(cursor)
    df = pd.DataFrame(data)
    return df

def fetch_roads(db, collection_name):
    cursor = db.aql.execute(
        f'FOR doc IN {collection_name} RETURN {{id: doc._key, geometry: doc.geometry}}',
        stream=True 
    )
    
    data = [record for record in cursor]
    df = pd.DataFrame(data)
    return df

def create_edges(db, df, col_1, col_2, collection_name = "edges_rel_1", new_column = None):
       
    if not db.has_collection(collection_name):
        edge_collection = db.create_collection(collection_name, edge=True)
    else:
        edge_collection = db.collection(collection_name)

    # edges = df.rename(columns={
    # 'id_left': '_from',
    # 'id_right': '_to'
    # })
    if new_column is None:
        edges = df[['id_left', 'id_right']]
    else:
        edges = df[['id_left', 'id_right', new_column]]
    edges['_from'] = edges['id_left']
    edges['_to'] = edges['id_right']

    edges['_from'] = edges['_from'].apply(lambda x: f"{col_1}/{x}")
    edges['_to'] = edges['_to'].apply(lambda x: f"{col_2}/{x}")

    if len(edges) > 100_000:
        batch_size = 10000 
        batches = np.array_split(edges, len(edges) // batch_size)
        
        for batch in tqdm(batches):
            try:
                res = edge_collection.insert_many(batch.to_dict(orient='records'), overwrite = True, silent = False)
            except Exception as e:
                print(e)
    else:
        try:
            res = edge_collection.insert_many(edges.to_dict(orient='records'), overwrite = True, silent = False)
        except Exception as e:
            print(e)

    print("Edges successfully added in bulk!")


def create_edges_7(db, df, col_1, col_2, collection_name = "edges_rel_7"):
       
    if not db.has_collection(collection_name):
        edge_collection = db.create_collection(collection_name, edge=True)
    else:
        edge_collection = db.collection(collection_name)

    
    edges = df[['id_left', 'id_right']]
    edges['_from'] = edges['id_left']
    edges['_to'] = edges['id_right']

    edges['_from'] = edges['_from'].apply(lambda x: f"{col_1}/{x}")
    edges['_to'] = edges['_to'].apply(lambda x: f"{col_2}/{x}")

    batch_size = 10000 
    batches = np.array_split(edges, len(edges) // batch_size)
    
    for batch in tqdm(batches):
        try:
            res = edge_collection.insert_many(batch.to_dict(orient='records'), overwrite = True, silent = False)
        except Exception as e:
            print(e)

    print("Edges successfully added in bulk!")