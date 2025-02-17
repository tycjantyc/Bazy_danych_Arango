
### 1. **Setting Up the Environment**

We started by importing the necessary libraries:

- **`ArangoClient`**
- **`shapely`**
- **`pandas`**
- **`tqdm`**
- **`os`**
- **`time`**

Additionally, we configured the database connection parameters (host, port, username, and password) using environment variables to enhance security and flexibility.

---

### 2. **Connecting to the Database**

We used the `ArangoClient` object to establish a connection to the `_system` database of ArangoDB with the credentials provided.

```
client = ArangoClient()
db = client.db('_system', username=ARANGO_USER, password=ARANGO_PASSWORD)
```

---

### 3. **Converting Geospatial Data**

A helper function, `wkt_to_geojson_vectorized`, was defined to:

- Take a column of geospatial data in WKT format from a Pandas DataFrame.
- Convert each WKT entry into GeoJSON format using the `shapely` library.

```python
def wkt_to_geojson_vectorized(wkt_series):
    return wkt_series.apply(lambda wkt_string: mapping(loads(wkt_string)))
```

---

### 4. **Importing Data**

We initially used the **`arangoimport`** as command line tool to bulk import the data. However data needs to be in json form to be imported so preprocessing and converting to json before importing was so time consuming that this approach wasn't viable. To overcome this, we switched to **`insert_many`**, to retrive chunked data and import all the data on the go instead of doing it at once. This significantly reduced import times and memory overhead during uploads.

The data import process also revealed challenges in handling large CSV files. To process files efficiently, we attempted to use the **Polars** library for chunking. Unfortunately, Polars doesn’t natively support retrieving only a chunk of data at a time; instead, it reads and outputs the entire DataFrame. Consequently, we reverted to using Pandas for chunk-based processing.

```
Uploading times of ads24-buildings.csv
Polars: 72.432
Pandas: 111.311
```

The core import function performs the following steps:
1. **Checking and Creating Collections**:
   - Verifies if the required collection exists in the database.
   - Creates the collection if it doesn’t exist.
2. **Reading CSV Files**:
   - Pandas reads data in chunks of 10,000 rows to avoid memory overload.
3. **Processing Geospatial Data**:
   - Converts the `wkt` column in each chunk to GeoJSON format.
4. **Uploading Data**:
   - Uploads data using `insert_many` for bulk upload.

---

### 5. **Geospatial Features and Data Structures**

The datasets we processed contained various types of geospatial features, which were stored in ArangoDB as follows:
- **Trees**: Stored as **points**, each representing a single location.
- **Communes, Powiats, and Voivodships**: Represented as **polygons**, each defining the boundaries of these administrative regions.
- **Roads and Railways**: Stored as **linestrings**, capturing the linear paths of transportation networks.

These distinctions were critical for ensuring accurate geospatial queries and analysis in ArangoDB.

---

### 6. **Dataset Details**

The script processed the following datasets, importing them into their respective collections in ArangoDB:

| **CSV File**            | **Target Collection** |
| ----------------------- | --------------------- |
| `ads24-buildings.csv`   | `buildings`           |
| `ads24-cities.csv`      | `cities`              |
| `ads24-communes.csv`    | `communes`            |
| `ads24-powiats.csv`     | `powiats`             |
| `ads24-voivodships.csv` | `voivodships`         |
| `ads24-countries.csv`   | `countries`           |
| `ads24-railways.csv`    | `railways`            |
| `ads24-trees.csv`       | `trees`               |
| `ads24-roads.csv`       | `roads`               |

---

### 7. **Logs**

Here’s the time it took to process and import each dataset:

```
File: data/ads24-buildings.csv Processing and Import time: 1736.25s
File: data/ads24-cities.csv Processing and Import time: 22.36s
File: data/ads24-communes.csv Processing and Import time: 9.88s
File: data/ads24-powiats.csv Processing and Import time: 3.73s
File: data/ads24-voivodships.csv Processing and Import time: 1.03s
File: data/ads24-countries.csv Processing and Import time: 0.42s
File: data/ads24-railways.csv Processing and Import time: 10.25s
File: data/ads24-trees.csv Processing and Import time: 50.02s
File: data/ads24-roads.csv Processing and Import time: 229.68s
```

---

### Conclusion

This project highlighted the challenges of processing large geospatial datasets and importing them into ArangoDB. Key takeaways include:
- Leveraging **insert_many** for efficient bulk uploads.
- Understanding the limitations of **Polars** for chunked data processing.
- Using appropriate data structures (points, polygons, and linestrings) for different geospatial features.

Despite these challenges, the workflow is robust and scalable for handling large, complex datasets.