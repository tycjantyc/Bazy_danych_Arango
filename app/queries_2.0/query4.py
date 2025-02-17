from arango import ArangoClient
import os
os.environ['USE_PYGEOS'] = '0'
import geopandas as gpd
import pandas as pd
from shapely.geometry import shape, Point
from utils import fetch_geometries_q_7, save_queries_result

ARANGO_HOST = os.getenv("ARANGO_HOST", "arangodb")
ARANGO_PORT = int(os.getenv("ARANGO_PORT", 8529))
ARANGO_USER = os.getenv("ARANGO_USER", "root")
ARANGO_PASSWORD = os.getenv("ARANGO_PASSWORD", "yourpassword")

client = ArangoClient()
db = client.db('_system', username=ARANGO_USER, password=ARANGO_PASSWORD)

max_distance = 500
min_size = 10

def fetch_geometries_q_4(db, edges_name, max_distance):
    """Fetch geometries from ArangoDB collection and convert to DataFrame."""
    query = f"""
    FOR edge IN {edges_name}
        FILTER edge.distance < {max_distance}
        LET left_tree = DOCUMENT("buildings", edge.id_left)
        LET right_tree = DOCUMENT("buildings", edge.id_right)
        RETURN {{
            id_f: edge.id_left,
            id_t: edge.id_right,
            distance: edge.distance,
            geom_f: left_tree.geometry,
            geom_t: right_tree.geometry
        }}
    """
    cursor = db.aql.execute(query) 
    data = list(cursor)
    df = pd.DataFrame(data)
    return df

df = fetch_geometries_q_4(db, "edges_rel_6", max_distance)

import networkx as nx

def create_graph_from_dataframe(df):
    G = nx.Graph()
    for _, row in df.iterrows():
        G.add_node(row['id_f'], geom = row['geom_f'])
        G.add_node(row['id_t'], geom = row['geom_t'])
        G.add_edge(row['id_f'], row['id_t'], distance=row['distance'])
    return G

def find_large_clusters(G, min_size=10):
    clusters = [comp for comp in nx.connected_components(G) if len(comp) >= min_size]
    return clusters

G = create_graph_from_dataframe(df)
large_clusters = find_large_clusters(G)

print(f"Liczba dużych klastrów: {len(large_clusters)}")

df = pd.Series(large_clusters)
save_queries_result(df, 'well')








