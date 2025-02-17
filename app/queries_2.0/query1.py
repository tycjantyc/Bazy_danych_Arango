from arango import ArangoClient
import os
os.environ['USE_PYGEOS'] = '0'
import geopandas as gpd
from sklearn.cluster import DBSCAN
import numpy as np
import pandas as pd
from shapely.geometry import shape
from utils import fetch_geometries, save_queries_result, exec_query

ARANGO_HOST = os.getenv("ARANGO_HOST", "arangodb")
ARANGO_PORT = int(os.getenv("ARANGO_PORT", 8529))
ARANGO_USER = os.getenv("ARANGO_USER", "root")
ARANGO_PASSWORD = os.getenv("ARANGO_PASSWORD", "yourpassword")

client = ArangoClient()
db = client.db('_system', username=ARANGO_USER, password=ARANGO_PASSWORD)

query = '''FOR commune IN communes
    LET cityCount = LENGTH(
        FOR city IN INBOUND commune edges_rel_1
            FILTER IS_SAME_COLLECTION('cities', city)
            RETURN city
    )
    RETURN { commune: commune.name, cityCount: cityCount }'''

df = exec_query(db, query)

save_queries_result(df, 'query1')