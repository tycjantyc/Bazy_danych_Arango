import geopandas as gpd
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
    """
    Perform a custom spatial join between two GeoDataFrames using a custom predicate function.

    Args:
        gdf1 (GeoDataFrame): The first GeoDataFrame.
        gdf2 (GeoDataFrame): The second GeoDataFrame.
        predicate_func (callable): A function that takes two geometries (geom1, geom2)
                                   and returns True or False based on the predicate.

    Returns:
        GeoDataFrame: Resulting GeoDataFrame after applying the custom join.
    """
    # Step 1: Build a spatial index for gdf2
    sindex = gdf2.sindex

    # Step 2: Iterate through geometries in gdf1
    matches = []
    for idx1, row1 in gdf1.iterrows():
        # Query gdf2's spatial index for potential matches (bounding box)
        possible_matches_idx = list(sindex.intersection(row1.geometry.bounds))
        possible_matches = gdf2.iloc[possible_matches_idx]

        # Apply the custom predicate function to filter the candidates
        for idx2, row2 in possible_matches.iterrows():
            if predicate_func(row1.geometry, row2.geometry):
                matches.append((idx1, idx2))  # Save matching indices

    # Step 3: Build a new DataFrame with the matches
    matches_df = pd.DataFrame(matches, columns=["gdf1_index", "gdf2_index"])
    result = matches_df.merge(gdf1.reset_index(), left_on="gdf1_index", right_on="index")
    result = result.merge(gdf2.reset_index(), left_on="gdf2_index", right_on="index", suffixes=("_gdf1", "_gdf2"))
    return gpd.GeoDataFrame(result, geometry="geometry_gdf1")

from shapely.geometry import LineString
import numpy as np

def are_lines_compatible(line1, line2, distance_threshold=100, angle_tolerance=1):
    # Step 1: Check if the lines are at least `distance_threshold` apart
    if line1.distance(line2) < distance_threshold:
        return False  # Lines are too close

    # Step 2: Vectorized calculation of segment angles
    def calculate_angles(coords):
        """
        Compute angles (in degrees) for each segment in a LineString.
        Args:
            coords (list): List of (x, y) coordinate tuples from a LineString.
        Returns:
            np.array: Array of angles (in degrees) for the segments.
        """
        coords = np.array(coords)
        deltas = coords[1:] - coords[:-1]  # Compute dx, dy for each segment
        angles = np.degrees(np.arctan2(deltas[:, 1], deltas[:, 0]))  # Compute angles
        return angles

    # Get angles for segments of both lines
    angles1 = calculate_angles(np.array(line1.coords))
    angles2 = calculate_angles(np.array(line2.coords))

    # Compute all pairwise angle differences (vectorized)
    angle_differences = np.abs(angles1[:, None] - angles2[None, :])  # Pairwise differences
    angle_differences = np.minimum(angle_differences, 360 - angle_differences)  # Handle circular angles

    # Step 3: Check if any angle differences are within the tolerance
    if np.any(angle_differences <= angle_tolerance):
        return False  # Parallel segments found

    # If all checks pass, return True
    return True


df = custom_sjoin(roads, rails, are_lines_compatible)

save_queries_result(df, 'q_6')