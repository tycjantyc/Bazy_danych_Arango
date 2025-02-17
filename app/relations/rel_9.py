from arango import ArangoClient
import os
os.environ['USE_PYGEOS'] = '0'
import geopandas as gpd
from shapely.geometry import shape, Point
from utils import fetch_geometries, create_edges, fetch_roads
import pandas as pd
import numpy as np

ARANGO_HOST = os.getenv("ARANGO_HOST", "arangodb")
ARANGO_PORT = int(os.getenv("ARANGO_PORT", 8529))
ARANGO_USER = os.getenv("ARANGO_USER", "root")
ARANGO_PASSWORD = os.getenv("ARANGO_PASSWORD", "yourpassword")

client = ArangoClient()
db = client.db('_system', username=ARANGO_USER, password=ARANGO_PASSWORD)

df = fetch_roads(db, "roads")

df['geometry'] = df['geometry'].apply(shape)
gdf = gpd.GeoDataFrame(df, geometry='geometry')

gdf['coords'] = gdf['geometry'].apply(lambda geom: list(geom.coords))
exploded = gdf.explode('coords', ignore_index=True)
exploded['coords'] = exploded['coords'].apply(Point)

print('Step2')


exploded['coords'] = exploded['coords'].apply(lambda point: (point.x, point.y))

node_counts = exploded.groupby('coords').size().reset_index(name='count')

shared_nodes = node_counts[node_counts['count'] > 1]['coords']
print('Step 3:', shared_nodes)

exploded = exploded[exploded['coords'].isin(shared_nodes)]

print('Step4')

exploded['road_id'] = exploded.index // exploded['coords'].map(len)

exploded['position'] = exploded.groupby('road_id').cumcount()

print('Step5')

exploded['prev_coords'] = exploded.groupby('road_id')['coords'].shift(1)
exploded['next_coords'] = exploded.groupby('road_id')['coords'].shift(-1)

relations = exploded[exploded['coords'].isin(shared_nodes)]

relations_df = relations[['road_id', 'coords', 'prev_coords', 'next_coords']]

relations_df = relations_df.dropna(subset=['prev_coords', 'next_coords'], how='all')

def parse_coords(coords):
    if pd.isna(coords):
        return np.nan  
    
    coords = str(coords)

    
    coords = coords.strip("()")  
    return tuple(map(float, coords.split(", ")))  

relations_df['coords'] = relations_df['coords'].apply(parse_coords)
relations_df['prev_coords'] = relations_df['prev_coords'].apply(parse_coords)
relations_df['next_coords'] = relations_df['next_coords'].apply(parse_coords)


agg_df = relations_df.groupby('road_id').agg({
    'coords': 'first',  
    'prev_coords': lambda x: next((i for i in x if pd.notna(i)), np.nan),  
    'next_coords': lambda x: next((i for i in x if pd.notna(i)), np.nan)   
}).reset_index()

print(agg_df)

create_edges(db, agg_df, 'roads', 'roads', 'edges_rel_9')







create_edges(db, df, 'roads', 'roads', 'edges_rel_9')