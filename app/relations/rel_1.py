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

voiv_df = fetch_geometries(db, "cities")
countries_df = fetch_geometries(db, "communes")

voiv_df['geometry'] = voiv_df['geometry'].apply(shape)
countries_df['geometry'] = countries_df['geometry'].apply(shape)

voiv_gdf = gpd.GeoDataFrame(voiv_df, geometry='geometry', crs='EPSG:4326')
countries_gdf = gpd.GeoDataFrame(countries_df, geometry='geometry', crs='EPSG:4326')

voiv_within_countries = gpd.sjoin(voiv_gdf, countries_gdf, predicate='within')

print(len(voiv_within_countries))

create_edges(db, voiv_within_countries, 'cities', 'communes', "edges_rel_1")