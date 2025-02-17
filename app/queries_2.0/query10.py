from arango import ArangoClient
import os
os.environ['USE_PYGEOS'] = '0'
import geopandas as gpd
import pandas as pd
from shapely.geometry import shape, Point, LineString
from utils import fetch_geometries_q_7, save_queries_result
import alphashape

ARANGO_HOST = os.getenv("ARANGO_HOST", "arangodb")
ARANGO_PORT = int(os.getenv("ARANGO_PORT", 8529))
ARANGO_USER = os.getenv("ARANGO_USER", "root")
ARANGO_PASSWORD = os.getenv("ARANGO_PASSWORD", "yourpassword")

client = ArangoClient()
db = client.db('_system', username=ARANGO_USER, password=ARANGO_PASSWORD)


def fetch_geometries_q_8(db, edges_name):
    """Fetch geometries from ArangoDB collection and convert to DataFrame."""
    query = f"""
    FOR edge IN {edges_name}
        LET left_tree = DOCUMENT("trees", edge.id_left)
        LET right_tree = DOCUMENT("roads", edge.id_right)
        RETURN {{
            id_f: edge.id_left,
            id_t: edge.id_right,
            geom_f: left_tree.geometry,
            geom_t: right_tree.geometry
        }}
    """
    cursor = db.aql.execute(query) 
    data = list(cursor)
    df = pd.DataFrame(data)
    return df

max_distance = 10
min_samples = 5

df = fetch_geometries_q_8(db, "edges_rel_8")

df['distance'] = pd.Series([Point(p['coordinates']).distance(LineString(q['coordinates'])) for p, q in zip(df['geom_f'], df['geom_t'])]) 
df = df[df['distance'] < max_distance]

g_df = df.groupby('id_t')['id_f'].count().reset_index()
g_df = g_df.rename(columns={'id_f': 'count'})
g_df = g_df[g_df['count'] > min_samples]

print(g_df.head())










