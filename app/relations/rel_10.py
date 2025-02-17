from arango import ArangoClient
import os
os.environ['USE_PYGEOS'] = '0'
import geopandas as gpd
from shapely.geometry import shape
from utils import fetch_geometries, create_edges
import pandas as pd
import numpy as np

ARANGO_HOST = os.getenv("ARANGO_HOST", "arangodb")
ARANGO_PORT = int(os.getenv("ARANGO_PORT", 8529))
ARANGO_USER = os.getenv("ARANGO_USER", "root")
ARANGO_PASSWORD = os.getenv("ARANGO_PASSWORD", "yourpassword")

client = ArangoClient()
db = client.db('_system', username=ARANGO_USER, password=ARANGO_PASSWORD)

gdf_railways = fetch_geometries(db, "railways")
gdf_roads = fetch_geometries(db, "roads")

gdf_railways['geometry'] = gdf_railways['geometry'].apply(shape)
gdf_roads['geometry'] = gdf_roads['geometry'].apply(shape)

gdf_railways = gpd.GeoDataFrame(gdf_railways, geometry='geometry', crs='EPSG:4326')
gdf_roads = gpd.GeoDataFrame(gdf_roads, geometry='geometry', crs='EPSG:4326')

gdf_railways.set_crs(epsg=4326, inplace=True)
gdf_roads.set_crs(epsg=4326, inplace=True)

def get_segment_at_point(linestring, point, buffer_distance=1e-6):
    
    point_buffer = point.buffer(buffer_distance)
    
    intersection = linestring.intersection(point_buffer)
    
    if intersection.is_empty:
        return None
    
    if intersection.geom_type == 'MultiLineString':
        intersection = max(intersection.geoms, key=lambda x: x.length)
    
    if intersection.geom_type != 'LineString':
        return None
        
    return intersection

def calculate_intersection_angle(railway_geom, road_geom):
    
    intersection_point = railway_geom.intersection(road_geom)
    if intersection_point.geom_type == 'MultiPoint':
        intersection_point = intersection_point.geoms[0]
    elif intersection_point.geom_type != 'Point':
        return None
    
    railway_segment = get_segment_at_point(railway_geom, intersection_point)
    road_segment = get_segment_at_point(road_geom, intersection_point)
    
    if railway_segment is None or road_segment is None:
        return None
    
    def get_vector(linestring):
        coords = list(linestring.coords)
        if len(coords) < 2:
            return None
        vector = np.array(coords[-1]) - np.array(coords[0])
        return vector / np.linalg.norm(vector)
    
    railway_vector = get_vector(railway_segment)
    road_vector = get_vector(road_segment)
    
    if railway_vector is None or road_vector is None:
        return None
    
    dot_product = np.clip(np.dot(railway_vector, road_vector), -1.0, 1.0)
    angle_rad = np.arccos(dot_product)
    angle_deg = np.degrees(angle_rad)
    
    return min(angle_deg, 180 - angle_deg)

intersections = gpd.sjoin(gdf_railways, gdf_roads, how='inner', predicate='intersects')

intersection_angles = []
for idx, row in intersections.iterrows():
    railway_geom = row['geometry']
    road_geom = gdf_roads.loc[row['index_right'], 'geometry']
    angle = calculate_intersection_angle(railway_geom, road_geom)
    intersection_angles.append(angle)

intersections['angle'] = intersection_angles

result_df = intersections[['id_left', 'id_right', 'angle']].copy()
result_df = result_df.dropna()

create_edges(db, result_df, 'railways', 'roads', 'edges_rel_10')

