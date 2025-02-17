import pandas as pd
import numpy as np
from tqdm import tqdm

def fetch_geometries(db, collection_name):
    """Fetch geometries from ArangoDB collection and convert to DataFrame."""
    collection = db.collection(collection_name)
    cursor = db.aql.execute(
        f'FOR doc IN {collection_name} RETURN {{id: doc._key,name: doc.name, geometry: doc.geometry}}'
    )
    
    data = list(cursor)
    df = pd.DataFrame(data)
    return df

def fetch_geometries_q_10(db, collection_name):
    """Fetch geometries from ArangoDB collection and convert to DataFrame."""
    collection = db.collection(collection_name)
    cursor = db.aql.execute(
        f'FOR doc IN {collection_name} RETURN {{id_f: doc.id_left,id_t: doc.id_right, angle: doc.angle}}'
    )
    
    data = list(cursor)
    df = pd.DataFrame(data)
    return df

def exec_query(db, query):
    cursor = db.aql.execute(query)
    data = list(cursor)
    df = pd.DataFrame(data)
    return df

def fetch_geometries_q_7(db, collection_name, max_distance):
    """Fetch geometries from ArangoDB collection and convert to DataFrame."""
    cursor = db.aql.execute(
        f'FOR doc IN {collection_name} FILTER doc.distance < {max_distance} RETURN {{id_f: doc.id_left,id_t: doc.id_right, distance: doc.distance}}'
    )
    
    data = list(cursor)
    df = pd.DataFrame(data)
    return df

def fetch_geometries_roads(db, collection_name):
    """Fetch geometries from ArangoDB collection and convert to DataFrame."""
    collection = db.collection(collection_name)
    cursor = db.aql.execute(
        f'FOR doc IN {collection_name} RETURN {{id: doc._key,oneway: doc.oneway, geometry: doc.geometry}}'
    )
    
    data = list(cursor)
    df = pd.DataFrame(data)
    return df

def fetch_roads(db, collection_name):
    cursor = db.aql.execute(
        f'FOR doc IN {collection_name} RETURN {{id: doc._key, geometry: doc.geometry}}',
        stream=True  # Enables the streaming cursor
    )
    
    data = [record for record in cursor]
    df = pd.DataFrame(data)
    return df

def create_edges(db, df, col_1, col_2, collection_name = "edges_rel_1"):
       
    if not db.has_collection(collection_name):
        edge_collection = db.create_collection(collection_name, edge=True)
    else:
        edge_collection = db.collection(collection_name)

    # edges = df.rename(columns={
    # 'id_left': '_from',
    # 'id_right': '_to'
    # })
    edges = df[['id_left', 'id_right']]
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


def save_queries_result(df, name:str):

    json_data = df.to_json(orient='records', indent=4)

    # file_path = f'{name}.json'
    # with open(file_path, 'w') as json_file:
    #     json_file.write(json_data)

    # print(f"JSON file saved to {file_path}")

    print(json_data)

def save_queries_result_7(df, name:str):

    json_data = df.to_json()
    print(json_data)