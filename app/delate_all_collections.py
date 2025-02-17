from arango import ArangoClient

def delete_all_collections(db_url, db_name, username, password):
    
    client = ArangoClient()
    sys_db = client.db('_system', username=username, password=password)
    
    if not sys_db.has_database(db_name):
        raise ValueError(f"Database '{db_name}' does not exist.")

    db = client.db(db_name, username=username, password=password)
    
    collections = db.collections()
    deleted_collections = []
    
    for collection in collections:
        if not collection['system']:  
            col_name = collection['name']
            db.delete_collection(col_name)
            deleted_collections.append(col_name)
    
    return deleted_collections
