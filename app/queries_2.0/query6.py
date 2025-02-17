from shapely.geometry import LineString
import pandas as pd
from arango import ArangoClient
import os
os.environ['USE_PYGEOS'] = '0'
import geopandas as gpd
from shapely.geometry import shape
from utils import fetch_geometries_roads, create_edges, save_queries_result, fetch_geometries

ARANGO_HOST = os.getenv("ARANGO_HOST", "arangodb")
ARANGO_PORT = int(os.getenv("ARANGO_PORT", 8529))
ARANGO_USER = os.getenv("ARANGO_USER", "root")
ARANGO_PASSWORD = os.getenv("ARANGO_PASSWORD", "yourpassword")

client = ArangoClient()
db = client.db('_system', username=ARANGO_USER, password=ARANGO_PASSWORD)

roads = fetch_geometries_roads(db, 'roads')
rails = fetch_geometries(db, 'railways')

roads['geometry'] = roads['geometry'].apply(shape)
roads = gpd.GeoDataFrame(roads, geometry='geometry', crs='EPSG:4326')
roads = roads.to_crs(crs = 2180)

rails['geometry'] = rails['geometry'].apply(shape)
rails = gpd.GeoDataFrame(rails, geometry='geometry', crs='EPSG:4326')
rails = rails.to_crs(crs = 2180)

def custom_sjoin(gdf1, gdf2, predicate_func):

    sindex = gdf2.sindex

    matches = []
    for idx1, row1 in gdf1.iterrows():
        possible_matches_idx = list(sindex.intersection(row1.geometry.bounds))
        possible_matches = gdf2.iloc[possible_matches_idx]

        for idx2, row2 in possible_matches.iterrows():
            if predicate_func(row1.geometry, row2.geometry):
                matches.append((idx1, idx2))  

    matches_df = pd.DataFrame(matches, columns=["gdf1_index", "gdf2_index"])
    result = matches_df.merge(gdf1.reset_index(), left_on="gdf1_index", right_on="index")
    result = result.merge(gdf2.reset_index(), left_on="gdf2_index", right_on="index", suffixes=("_gdf1", "_gdf2"))
    return gpd.GeoDataFrame(result, geometry="geometry_gdf1")

from shapely.geometry import LineString
import numpy as np

def are_lines_compatible(line1, line2, distance_threshold=100, angle_tolerance=1):
    if line1.distance(line2) < distance_threshold:
        return False  

    def calculate_angles(coords):
        coords = np.array(coords)
        deltas = coords[1:] - coords[:-1] 
        angles = np.degrees(np.arctan2(deltas[:, 1], deltas[:, 0]))  
        return angles

    angles1 = calculate_angles(np.array(line1.coords))
    angles2 = calculate_angles(np.array(line2.coords))

    angle_differences = np.abs(angles1[:, None] - angles2[None, :])
    angle_differences = np.minimum(angle_differences, 360 - angle_differences)

    if np.any(angle_differences <= angle_tolerance):
        return False  

    return True


df = custom_sjoin(roads, rails, are_lines_compatible)

save_queries_result(df, 'q_6')