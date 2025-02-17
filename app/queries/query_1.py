from arango import ArangoClient
import os
os.environ['USE_PYGEOS'] = '0'
import geopandas as gpd
from shapely.geometry import shape
from utils import fetch_geometries, create_edges, save_queries_result

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

voiv_within_countries = gpd.sjoin(countries_gdf, voiv_gdf, predicate='within')

df = voiv_within_countries[['name_left', 'name_right']]

grouped_df = df.groupby('name_left')['name_right'].count().reset_index()
grouped_df = grouped_df.rename(columns={'name_right': 'count'})

print(len(grouped_df))
save_queries_result(grouped_df, 'q_1')
