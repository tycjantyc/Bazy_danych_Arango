from arango import ArangoClient
import os
os.environ['USE_PYGEOS'] = '0'
import geopandas as gpd
from shapely.geometry import shape
from utils import fetch_geometries_build, create_edges
from scipy.spatial import cKDTree
import numpy as np

ARANGO_HOST = os.getenv("ARANGO_HOST", "arangodb")
ARANGO_PORT = int(os.getenv("ARANGO_PORT", 8529))
ARANGO_USER = os.getenv("ARANGO_USER", "root")
ARANGO_PASSWORD = os.getenv("ARANGO_PASSWORD", "yourpassword")

client = ArangoClient()
db = client.db('_system', username=ARANGO_USER, password=ARANGO_PASSWORD)

buildings_df = fetch_geometries_build(db, "buildings", 10000)
buildings_df['geometry'] = buildings_df['geometry'].apply(shape)

buildings_gdf = gpd.GeoDataFrame(buildings_df, geometry='geometry', crs='EPSG:4326')

buildings_gdf = buildings_gdf.to_crs(epsg=3857)
centroids = buildings_gdf.geometry.centroid

coords = centroids.apply(lambda geom: (geom.x, geom.y)).to_list()
tree = cKDTree(coords)

print("Before pairing")
pairs = tree.query_pairs(r=500, output_type='ndarray')
print("After pairing")

df = gpd.GeoDataFrame({
    'id_left': np.array((buildings_gdf.iloc[pairs[:, 0]]['id'])),
    'id_right': np.array((buildings_gdf.iloc[pairs[:, 1]]['id'])),
    'geo1': np.array((buildings_gdf.iloc[pairs[:, 0]]['geometry'])),
    'geo2': np.array((buildings_gdf.iloc[pairs[:, 1]]['geometry']))
})

df['distance'] = df.apply(lambda row: row['geo1'].distance(row['geo2']), axis=1)

create_edges(db, df, 'buildings', 'buildings', "edges_rel_6", "distance")

print(f"Created {len(df)} building relationships within 500m")