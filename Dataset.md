## **1. Data Analysis**

### **Dataset Summary**

The provided datasets contain spatial and attribute data in CSV format. Each dataset is briefly analyzed below:

1. **Buildings**
   - **Key Attributes** : `id`, `building`
   - **Geometry** : LINESTRING in WKT format (stored as GeoJSON during processing).
   - Represents building outlines with attributes indicating usage (e.g., `building=yes`).
2. **Cities**
   - **Key Attributes** : `id`, `name`
   - **Geometry** : LINESTRING in WKT format.
   - Represents city boundaries.
3. **Communes**
   - **Key Attributes** : `id`, `name`
   - **Geometry** : LINESTRING or MULTILINESTRING in WKT format.
   - Represents commune boundaries.
4. **Powiats**
   - **Key Attributes** : `id`, `name`
   - **Geometry** : LINESTRING or MULTILINESTRING in WKT format.
   - Represents powiat boundaries.
5. **Countries**
   - **Key Attributes** : `id`, `name`
   - **Geometry** : LINESTRING in WKT format.
   - Represents country boundaries.
6. **Voivodships**
   - **Key Attributes** : `id`, `name`
   - **Geometry** : LINESTRING or MULTILINESTRING in WKT format.
   - Represents voivodship boundaries.
7. **Railways**
   - **Key Attributes** : `id`, `railway`
   - **Geometry** : LINESTRING in WKT format.
   - Represents railway lines, with distinction betwen `rail` or `dismantled`.
8. **Trees**
   - **Key Attributes** : `id`
   - **Geometry** : POINT in WKT format.
   - Represents individual tree locations.
9. **Roads**
   - **Key Attributes** : `id`, `name`, `road_class`, `lanes`, `oneway`
   - **Geometry** : LINESTRING in WKT format.
   - Represents roads with additional attributes such as road type and node connections.

---

## **2. Implementation Plan**

### **Step 1: Data Preprocessing**

**Objective** : Prepare the datasets for integration into ArangoDB by cleaning, transforming, and converting geometry data.

1. **Data Cleaning**
   - Remove missing or invalid geometries using Python (`pandas` and `shapely`).
   - Code:
     ```python
     df = df[df['wkt'].notnull()]
     ```
2. **Geometry Conversion**
   - Convert WKT to GeoJSON for compatibility with ArangoDB.
   - Using Shapely for wkt to geometry conversion:
     ```python
     from shapely.wkt import loads
     from shapely.geometry import mapping
     df['geojson'] = df['wkt'].apply(lambda x: mapping(loads(x)))
     ```
3. **Changing coordinate system**
   - Ensure all geometries are in the ETRS89 coordinate system (EPSG:2180).
   - Use GeoPandas for reprojection:
     ```python
     import geopandas as gpd
     gdf = gpd.GeoDataFrame(df, geometry=df['wkt'].apply(loads), crs="EPSG:4326")
     gdf = gdf.to_crs("EPSG:2180")
     ```

---

### **Step 2: Database Design**

**Objective** : Define the collections, relationships, and schema for the ArangoDB database.

1. **Entity Collections**
   Each dataset corresponds to a collection in ArangoDB:

   - **`buildings`** : Stores building outlines.
   - **`cities`** : Stores city data.
   - **`communes`** : Stores commune boundaries.
   - **`powiats`** : Stores powiat boundaries.
   - **`voivodships`** : Stores voivodship boundaries.
   - **`countries`** : Stores country boundaries.
   - **`railways`** : Stores railway lines.
   - **`trees`** : Stores tree locations.
   - **`roads`** : Stores road geometries.

   Example Document for `buildings`:

   ```json
   {
     "_key": "building201782706",
     "id": 201782706,
     "building": "yes",
     "geojson": {
       "type": "LineString",
       "shape": ((18.9918839, 50.1900409), (18.9919257, 50.1900398), (18.991923200000002, 50.1899923), (18.9918811, 50.1899932), (18.9918839, 50.1900409))
     }
   }
   ```

2. **Edge Collections**
   Model relationships as edges:

   - `cities_within_communes`: Cities contained in communes.
   - `communes_within_powiats`: Communes contained in powiats.
   - `powiats_within_voivodships`: Powiats contained in voivodships.
   - `neighboring_communes`: Adjacent communes.
   - `roads_near_trees`: Trees near roads (within a threshold distance).

   Example Edge for `cities_within_communes`:

   ```json
   {
     "_from": "cities/city165941",
     "_to": "communes/commune295516",
     "relationship": "within"
   }
   ```

3. **Indexes**

   - **Spatial Indexes** : For `geojson` fields in all collections.
   - **Attribute Indexes** : For `id`, `name`, or other query-critical attributes.

---

### **Step 3: Data Import**

**Objective** : Load preprocessed data into ArangoDB.

1. Use ArangoDB’s HTTP API or `arangosh` for bulk insertion.
2. Example Python script for import:
   ```python
   import requests
   headers = {'Content-Type': 'application/json'}
   url = 'http://localhost:8529/_api/document/buildings'
   data = df.to_dict(orient='records')
   for record in data:
       requests.post(url, headers=headers, json=record)
   ```

---

### **Step 4: Relationship Detection**

**Objective** : Detect and materialize spatial relationships.

1. **Cities Within Communes**
   - Use spatial containment (`within`) from Shapely or GeoPandas.
   - Store results in `cities_within_communes`.
2. **Neighboring Entities**
   - Use spatial operations like `touches` or `distance`.
   - Example: Neighboring communes:
     ```python
     if commune1.geometry.touches(commune2.geometry):
         # Add to neighboring_communes edge collection
     ```
3. **Roads Near Trees**
   - Calculate distances between points (trees) and lines (roads).
   - Example:
     ```python
     if tree.geometry.distance(road.geometry) <= threshold:
         # Add to roads_near_trees edge collection
     ```


### **Remarks on the envoirnment** ###

1. We use docker compose with one container for ArangoDB and other for Python code
2. Set up docker with: docker-compose up --build
   Docker is running the database on localhost, installing dependencies for python code, and running the app in order to import the data and get ready for processing.

3. Design details are located in docker-compose.yml