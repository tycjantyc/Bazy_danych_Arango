from arango import ArangoClient
import os
os.environ['USE_PYGEOS'] = '0'
import geopandas as gpd
from sklearn.cluster import DBSCAN
import numpy as np
import pandas as pd
from shapely.geometry import shape, LineString, Point
from utils import fetch_geometries_roads, save_queries_result_7

ARANGO_HOST = os.getenv("ARANGO_HOST", "arangodb")
ARANGO_PORT = int(os.getenv("ARANGO_PORT", 8529))
ARANGO_USER = os.getenv("ARANGO_USER", "root")
ARANGO_PASSWORD = os.getenv("ARANGO_PASSWORD", "yourpassword")

client = ArangoClient()
db = client.db('_system', username=ARANGO_USER, password=ARANGO_PASSWORD)

min_samples, max_distance = 10, 10

roads = fetch_geometries_roads(db, "roads")

roads['geometry'] = roads['geometry'].apply(shape)
roads = gpd.GeoDataFrame(roads, geometry='geometry', crs='EPSG:4326')

roads = roads.to_crs(crs = 2180)

oneway_roads = roads[roads['oneway'] == 'yes']

def is_quasiroundabout(group):
    endpoints = []
    for geom in group.geometry:
        if isinstance(geom, LineString):
            # Add start and end points of each linestring
            endpoints.append(Point(geom.coords[0]))
            endpoints.append(Point(geom.coords[-1]))
    # Check if the start and end points collectively form a closed loop
    union_points = gpd.GeoSeries(endpoints).unary_union
    return union_points.is_ring  # Returns True if endpoints form a closed loop

buffered_roads = oneway_roads.copy()
buffered_roads['buffer'] = buffered_roads.geometry.buffer(100)  # Small buffer distance
groups = buffered_roads.dissolve(by='buffer').reset_index()

print('ok')
# Filter groups that form quasiroundabouts
roundabout_groups = groups[groups.geometry.apply(is_quasiroundabout)]
print('OK2')

print(type(roundabout_groups))
print(roundabout_groups)

# # Step 3: Extract IDs of the roads that form quasiroundabouts
# roundabout_ids = oneway_roads[oneway_roads.geometry.isin(roundabout_groups.geometry)]['id']

# # Print the IDs of roads forming a quasiroundabout
# print(roundabout_ids.tolist())
