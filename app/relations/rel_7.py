from arango import ArangoClient
import os
os.environ['USE_PYGEOS'] = '0'
import geopandas as gpd
from shapely.geometry import shape
from utils import fetch_geometries, create_edges, create_edges_7
from scipy.spatial import cKDTree
import numpy as np

ARANGO_HOST = os.getenv("ARANGO_HOST", "arangodb")
ARANGO_PORT = int(os.getenv("ARANGO_PORT", 8529))
ARANGO_USER = os.getenv("ARANGO_USER", "root")
ARANGO_PASSWORD = os.getenv("ARANGO_PASSWORD", "yourpassword")

client = ArangoClient()
db = client.db('_system', username=ARANGO_USER, password=ARANGO_PASSWORD)

trees_df = fetch_geometries(db, "trees")

trees_df['geometry'] = trees_df['geometry'].apply(shape)
trees_gdf = gpd.GeoDataFrame(trees_df, geometry='geometry', crs='EPSG:4326')

trees_gdf = trees_gdf.to_crs(epsg=3857) 
coords = trees_gdf.geometry.apply(lambda geom: (geom.x, geom.y)).to_list()
tree = cKDTree(coords)

print("GO!")
pairs = tree.query_pairs(r=50, output_type = 'ndarray')
print("End!")

print(len(pairs))
df = gpd.GeoDataFrame({'id_left': np.array((trees_gdf.iloc[pairs[:,0]]['id'])), 'id_right': np.array((trees_gdf.iloc[pairs[:,1]]['id'])),'geo1': np.array((trees_gdf.iloc[pairs[:,0]]['geometry'])), 'geo2': np.array((trees_gdf.iloc[pairs[:,1]]['geometry']))})
ser1 = gpd.GeoSeries(np.array((trees_gdf.iloc[pairs[:,0]]['geometry'])))
ser2 = gpd.GeoSeries(np.array((trees_gdf.iloc[pairs[:,1]]['geometry'])))
df['distance'] = ser1.distance(ser2)

create_edges_7(db, df,'trees', 'trees', "edges_rel_7")