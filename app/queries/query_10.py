from arango import ArangoClient
import os
os.environ['USE_PYGEOS'] = '0'
import geopandas as gpd
from sklearn.cluster import DBSCAN
import numpy as np
import pandas as pd
from shapely.geometry import shape, LineString, Point
from utils import fetch_geometries_roads, save_queries_result_7, fetch_geometries

ARANGO_HOST = os.getenv("ARANGO_HOST", "arangodb")
ARANGO_PORT = int(os.getenv("ARANGO_PORT", 8529))
ARANGO_USER = os.getenv("ARANGO_USER", "root")
ARANGO_PASSWORD = os.getenv("ARANGO_PASSWORD", "yourpassword")

client = ArangoClient()
db = client.db('_system', username=ARANGO_USER, password=ARANGO_PASSWORD)

min_samples, max_distance = 10, 10

roads = fetch_geometries_roads(db, "roads")
trees = fetch_geometries(db, 'trees')

trees['geometry'] = trees['geometry'].apply(shape)
roads['geometry'] = roads['geometry'].apply(shape)

roads = gpd.GeoDataFrame(roads, geometry='geometry', crs='EPSG:4326')
trees = gpd.GeoDataFrame(trees, geometry='geometry', crs='EPSG:4326')
roads = roads.to_crs(crs = 2180)
trees = trees.to_crs(crs = 2180)

roads['buffer'] = roads.geometry.buffer(max_distance)
roads['good_or_nah'] = pd.Series(np.zeros(len(roads)))

joined = gpd.sjoin(trees, roads, how="left", predicate="within")

grouped_joined = joined.groupby('id_right')['id_left'].count().reset_index()
grouped_joined = grouped_joined.rename(columns={'id_left': 'count'})
grouped_joined = grouped_joined[grouped_joined['count'] > min_samples]

print(len(grouped_joined))
save_queries_result_7(grouped_joined, 'q_10')
