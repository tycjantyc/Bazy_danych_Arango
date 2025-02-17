from arango import ArangoClient
import os
os.environ['USE_PYGEOS'] = '0'
import geopandas as gpd
from sklearn.cluster import DBSCAN
import numpy as np
import pandas as pd
from shapely.geometry import shape
from utils import fetch_geometries, save_queries_result_7

ARANGO_HOST = os.getenv("ARANGO_HOST", "arangodb")
ARANGO_PORT = int(os.getenv("ARANGO_PORT", 8529))
ARANGO_USER = os.getenv("ARANGO_USER", "root")
ARANGO_PASSWORD = os.getenv("ARANGO_PASSWORD", "yourpassword")

client = ArangoClient()
db = client.db('_system', username=ARANGO_USER, password=ARANGO_PASSWORD)

min_samples, max_distance = 10, 10

trees = fetch_geometries(db, "trees")

trees["geometry"] = trees["geometry"].apply(shape)
gdf = gpd.GeoDataFrame(trees, geometry="geometry",crs='EPSG:4326')
gdf = gdf.to_crs(epsg=2180) 


coords = np.array(gdf.geometry.apply(lambda x: (x.x, x.y)).tolist())


print("Start")
db = DBSCAN(eps=max_distance, min_samples=min_samples, metric='euclidean').fit(np.radians(coords))
print("End")

# Assign the clusters to the GeoDataFrame
gdf["cluster"] = db.labels_

convex_hulls = gdf.groupby('cluster').geometry.apply(lambda x: x.unary_union.convex_hull)

#convex_hulls = convex_hulls[convex_hulls['cluster'] != -1]
convex_hulls = convex_hulls.drop(convex_hulls.index[-1])

df = gpd.GeoDataFrame(convex_hulls)

print(len(convex_hulls))
save_queries_result_7(df, 'trees_queries')

