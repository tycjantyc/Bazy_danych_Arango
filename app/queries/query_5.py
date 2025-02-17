from arango import ArangoClient
import os
os.environ['USE_PYGEOS'] = '0'
import geopandas as gpd
from shapely.geometry import shape
from utils import fetch_geometries_q_10, create_edges, save_queries_result

ARANGO_HOST = os.getenv("ARANGO_HOST", "arangodb")
ARANGO_PORT = int(os.getenv("ARANGO_PORT", 8529))
ARANGO_USER = os.getenv("ARANGO_USER", "root")
ARANGO_PASSWORD = os.getenv("ARANGO_PASSWORD", "yourpassword")

client = ArangoClient()
db = client.db('_system', username=ARANGO_USER, password=ARANGO_PASSWORD)

max_angle = 80
min_angle = 77

communes_df = fetch_geometries_q_10(db, "edges_rel_10")

df = communes_df[communes_df['angle']>min_angle]
df = df[df['angle']<max_angle]
save_queries_result(df, 'angles')
print(len(df))




