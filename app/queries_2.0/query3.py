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

query = '''FOR voivodship IN voivodships
    LET adjacentVoivodships = UNIQUE(
        FOR powiat IN INBOUND voivodship edges_rel_3 
            FOR commune IN INBOUND powiat edges_rel_2 
                FOR neighborCommune IN OUTBOUND commune edges_rel_5 
                    FOR neighborPowiat IN OUTBOUND neighborCommune edges_rel_2 
                        FOR neighborVoivodship IN OUTBOUND neighborPowiat edges_rel_3 
                            FILTER IS_SAME_COLLECTION('voivodships', neighborVoivodship) AND neighborVoivodship._id != voivodship._id
                            RETURN neighborVoivodship.name
    )
    RETURN { voivodship: voivodship.name, adjacentVoivodships: adjacentVoivodships }

'''

df = exec_query(db, query)

save_queries_result(df, 'query1')
