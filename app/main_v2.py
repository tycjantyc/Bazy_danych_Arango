from arango import ArangoClient
import os
from shapely.wkt import loads
from shapely.geometry import mapping
from tqdm import tqdm
import pandas as pd
import time 
from shapely.wkt import loads
from shapely.geometry import mapping, Polygon,MultiPolygon, MultiLineString, LineString

ARANGO_HOST = os.getenv("ARANGO_HOST", "arangodb")
ARANGO_PORT = int(os.getenv("ARANGO_PORT", 8529))
ARANGO_USER = os.getenv("ARANGO_USER", "root")
ARANGO_PASSWORD = os.getenv("ARANGO_PASSWORD", "yourpassword")

# Initialize the ArangoDB client
client = ArangoClient()
db = client.db('_system', username=ARANGO_USER, password=ARANGO_PASSWORD)

def wkt_to_geojson_vectorized(wkt_series):
    """Convert a pandas Series of WKT LINESTRINGs to GeoJSON."""
    return wkt_series.apply(lambda wkt_string: mapping(loads(wkt_string)))

def wkt_to_geojson_polygon_bulk(wkt_series):
    wkt_series = wkt_series.apply(loads)
    wkt_series = wkt_series.apply(lambda geom: Polygon(list(geom.coords)) if isinstance(geom, LineString) else 
                                    MultiPolygon([Polygon(list(line.coords)) for line in geom.geoms]) if isinstance(geom, MultiPolygon) else geom)
    return wkt_series.apply(mapping)

def ccc_pow_voiv_prepare(chunk):
    chunk['geometry'] =  wkt_to_geojson_polygon_bulk(chunk['wkt'])
    return chunk[['id','name', 'geometry']].to_dict(orient='records')

def roads_prepare(chunk):
    chunk['geometry'] =  wkt_to_geojson_vectorized(chunk['wkt'])
    return chunk[['id', 'name', 'oneway', 'geometry']].to_dict(orient='records')

def railways_prepare(chunk):
    chunk['geometry'] =  wkt_to_geojson_vectorized(chunk['wkt'])
    return chunk[['id','geometry']].to_dict(orient='records')

def trees_prepare(chunk):
    chunk['geometry'] =  wkt_to_geojson_vectorized(chunk['wkt'])
    return chunk[['id','geometry']].to_dict(orient='records')

def building_prepare(chunk):
    chunk['geometry'] =  wkt_to_geojson_polygon_bulk(chunk['wkt'])
    return chunk[['id','geometry']].to_dict(orient='records')

def import_csv_to_collection(file_path, collection_name):

    if collection_name in ["cities", "communes", "countries", "powiats", "voivodships"]:
        data_process = ccc_pow_voiv_prepare
    elif collection_name in ["roads"]:
        data_process = roads_prepare
    elif collection_name in ["railways"]:
        data_process = railways_prepare
    elif collection_name in ["trees"]:
        data_process = trees_prepare
    elif collection_name in ["buildings"]:
        data_process = building_prepare
     
    
    time0 = time.time()
    if not db.has_collection(collection_name):
        db.create_collection(collection_name)
    collection = db.collection(collection_name)

    for chunk in tqdm(pd.read_csv(file_path, chunksize=10000)):
        
        try:
            documents = data_process(chunk)

            time1 = time.time()
            
            if collection_name == "roads":
                for doc in documents:
                    doc['name'] = None

                    if doc['oneway'] != doc['oneway']:
                        doc['oneway'] = 'no'

            print(documents[0])
            collection.insert_many(documents, overwrite=True)
            print(f"Uploaded {len(documents)} documents in {time.time() - time1}.")
        except Exception as e:
            print(f"Error processing chunk: {e}")
            

    return (time.time() - time0)
if __name__ == "__main__":

    datasets = [
        {"file": "data/ads24-buildings.csv", "collection": "buildings"},
        {"file": "data/ads24-cities.csv", "collection": "cities"},
        {"file": "data/ads24-communes.csv", "collection": "communes"},
        {"file": "data/ads24-powiats.csv", "collection": "powiats"},
        {"file": "data/ads24-voivodships.csv", "collection": "voivodships"},
        {"file": "data/ads24-countries.csv", "collection": "countries"},
        {"file": "data/ads24-railways.csv", "collection": "railways"},
        {"file": "data/ads24-trees.csv", "collection": "trees"},
        {"file": "data/ads24-roads.csv", "collection": "roads"}
    ]

    times = []

    for dataset in datasets:
        print(f"Starting importing: {dataset}")
        time_temp = import_csv_to_collection(dataset["file"], dataset["collection"])
        times.append(time_temp)
        print(f"Ended importing: {dataset}")
    
    for t, dataset in zip(times, datasets):
        print(f"File: {dataset['file']} Processing and Import time: {t}")


