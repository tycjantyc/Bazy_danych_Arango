from arango import ArangoClient
import os
os.environ['USE_PYGEOS'] = '0'
import geopandas as gpd
from shapely.geometry import shape
from utils import fetch_geometries, create_edges, fetch_roads

ARANGO_HOST = os.getenv("ARANGO_HOST", "arangodb")
ARANGO_PORT = int(os.getenv("ARANGO_PORT", 8529))
ARANGO_USER = os.getenv("ARANGO_USER", "root")
ARANGO_PASSWORD = os.getenv("ARANGO_PASSWORD", "yourpassword")

client = ArangoClient()
db = client.db('_system', username=ARANGO_USER, password=ARANGO_PASSWORD)

trees = fetch_geometries(db, "trees")
print("Trees uploaded!")
roads = fetch_roads(db, "roads")
print("Roads uploaded!")

trees['geometry'] = trees['geometry'].apply(shape)
roads['geometry'] = roads['geometry'].apply(shape)

trees = gpd.GeoDataFrame(trees, geometry='geometry', crs='EPSG:4326')
roads = gpd.GeoDataFrame(roads, geometry='geometry', crs='EPSG:4326')

trees = trees.to_crs("EPSG:3857")
roads = roads.to_crs("EPSG:3857")

roads['buffer'] = roads.geometry.buffer(20) 

trees = trees.set_geometry('geometry')
roads = roads.set_geometry('buffer')

trees_near_roads = gpd.sjoin(trees, roads[['id', 'buffer']], how='inner', predicate='within')

create_edges(db, trees_near_roads, 'trees', 'roads', 'edges_rel_10')