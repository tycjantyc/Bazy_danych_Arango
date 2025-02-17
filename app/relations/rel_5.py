from arango import ArangoClient
import os
os.environ['USE_PYGEOS'] = '0'
import geopandas as gpd
from shapely.geometry import shape
from utils import fetch_geometries, create_edges

ARANGO_HOST = os.getenv("ARANGO_HOST", "arangodb")
ARANGO_PORT = int(os.getenv("ARANGO_PORT", 8529))
ARANGO_USER = os.getenv("ARANGO_USER", "root")
ARANGO_PASSWORD = os.getenv("ARANGO_PASSWORD", "yourpassword")

client = ArangoClient()
db = client.db('_system', username=ARANGO_USER, password=ARANGO_PASSWORD)

communes_df = fetch_geometries(db, "communes")

communes_df['geometry'] = communes_df['geometry'].apply(shape)

communes_gdf = gpd.GeoDataFrame(communes_df, geometry='geometry', crs='EPSG:4326')

communes_nei_communes = gpd.sjoin(communes_gdf, communes_gdf, predicate='intersects')

print(len(communes_nei_communes))

create_edges(db, communes_nei_communes,'communes', 'communes', "edges_rel_5")

