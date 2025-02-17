# **Final Report**

## **Technology Choice**

We chose the following tools for our project:

* **ArangoDB** – A NoSQL database that combines relational and non-relational capabilities, making it well-suited for handling both document and graph-based data.
* **GeoPandas** – A Python library used for manipulating spatial data, essential for processing geographic relationships.
* **NetworkX** – A Python library designed for graph-based data operations, helping with the analysis of spatial relationships.

## **Prerequisites**

* **Docker Compose** installed
* **Python** version **3.10** or higher

## **System Architecture**

1. **Data Storage**
   * Data is stored in **ArangoDB collections** after being imported using `main2.py` (located in the `app` folder).
2. **Relationship Detection**
   * Spatial relationships between data entities are detected using  **custom Python scripts** . These scripts are located in `app/relations/` and can be executed as a  **CLI tool** .
3. **Query Execution**
   * Queries are performed using **AQL (Arango Query Language)** combined with  **basic Pandas processing** . Query-related scripts are stored in `app/queries_2.0/`.

## **Deployment Instructions**

To deploy the project, clone the repository and run:

```
docker-compose up --build
```

To run a specific script inside the Docker container:

```
docker exec -it python-app python /app/{file_name.py}
```

### **Key scripts**

* **Database Initialization** – `app/main_v2.py`
* **Query Execution Tool** – `app/queries_2.0/cli_tool_queries.py`
* **Relationship Detection Tool** – `app/rel/cli_tool_rel.py`

After calling the  **relationship or query tool** , specify the relationship or query number to execute the desired operation.

## **Manuals for CLI Tools**

### **Running Relationship Detection**

To execute a specific relationship detection, run:

```
python cli_tool_rel.py {relationship_number}
```

For example, to detect  **cities within communes (Relationship 1)** :

```
python cli_tool_rel.py 1
```

The execution time for the process will be displayed after completion.

### **Running Queries**

Similar to relationship detection, queries can be executed using:

```
python cli_tool_queries.py {query_number}
```

To modify  **query parameters** , manually update the corresponding Python file.

## **Timeline of Design and Development**

* **16.12** – Implemented **database import**
* **09.01** – Implemented **relationship detection**
* **23.01** – Implemented **query execution**
* **26.01** – Revised and optimized **queries**

## **Division of Tasks Among Project Members**

* **Jan Tyc** – Responsible mostly for **data import and queries**
* **Bartłomiej Tarcholik** – Responsible mostly for **data modeling and relationship detection**

## **Data Import**

* **Tools Used**: Python-Arango (`insert_many()` function)
* **Challenges**: The biggest challenge was converting **geospatial data to GeoJSON** format correctly. This required a complex function with multiple conditional checks.
* **Import Performance**:
* **Buildings Import** : ~40 minutes
* **Total Import Time** : ~55 minutes

## **Spatial Relationship Detection**

* **Tools Used** : GeoPandas, cKDTree, and custom Python functions
* **Detected Relationships** : **9 out of 10** were successfully implemented
* **Issue** : **Relationship 6** (neighboring buildings within 500 meters) took too long to process and did not converge.

### **Performance of Relationship Detection**

| Relationship                              | Execution Time (seconds) |
| ----------------------------------------- | ------------------------ |
| **1**(Cities within communes)       | 112.21                   |
| **2**(Communes within powiats)      | 50.28                    |
| **3**(Powiats within voivodships)   | 20.49                    |
| **4**(Voivodships within countries) | 7.83                     |
| **5**(Adjacent communes)            | 23.41                    |
| **6**(Buildings near each other)(only 100k buildings)    | 658.43
| **7**(Neighboring trees within 50m) | 813.46                   |
| **8**(Trees within 20m of roads)    | 1878.11                  |
| **9**(Roads connected by nodes)     | 2203.87                  |
| **10**(Railways crossing roads)     | 90.78                    |
| **Total Time**                      | ~1 hour 20 minutes       |

## **Storage of Detected Relationships**

* **Data Structure** : Relationships are stored as **edges** in ArangoDB.
* **Schema** :
* `_from` – Reference to the **source** entity (e.g., `"railways/8988738"`).
* `_to` – Reference to the **destination** entity.
* **Attributes** – Additional metadata like **distance or angle** (if applicable).
* **Import Performance** :
* **10,000 edges** – **0.25 to 1 second** (depending on processing mode).
* **Tree relationships (8 million edges)** –  **7 minutes** .

## **Query Implementation**

### **Executed Queries**

* Queries  **1-3, 5** : Fully implemented using **AQL**
<<<<<<< HEAD
* **Query 4,6** : Implemented in **Python** because necessary information was not directly available in relationships
=======
>>>>>>> f03a110ee18bc1d390a10c8c2279a803a2802578
* **Query 7 & 10** : Import data from relationships into Python to create **concave hulls**

### **Missing Queries and Issues**

* **Query 8 (Shortest Path Between Roads)** – **Not implemented**
* **Query 9 (Quasi-Roundabouts)** – **Not implemented**

### **Query Execution Performance**

| Query                                      | Execution Time |
| ------------------------------------------ | -------------- |
| **1**– Number of cities per commune | 10s            |
| **2**– Adjacent powiats             | 23s            |
| **3**– Adjacent voivodships         | 70s            |
| **4**- Buildings clusters           | 34s            |
| **5**– Road/Railway crossings       | 10s            |
| **6**– Parallel roads/railways      | 17 minutes     |
| **7**– Tree clusters                | 90s            |
| **10**– Roads with nearby trees     | 64s            |

## **Project Challenges and Justifications for Missing Components**

1. **Relationship 6 (Neighboring Buildings within 500m)**
   * This relationship took **too long to compute** and was unable to converge within a reasonable time.
   * Optimizations attempted included **parallel processing** and  **spatial indexing** , but they did not fully resolve the issue.
2. **Query 8 (Shortest Path Between Roads)**
   * The dataset lacked a  **pre-built road graph** , making shortest path computations infeasible within the given time constraints.
3. **Query 9 (Quasi-Roundabouts)**
   * Detecting **cycles in one-way roads** required a **custom graph traversal algorithm** that was not implemented in time.

## **Final Thoughts**

The project successfully implemented **9 out of 10 spatial relationships** and  **7 out of 10 required queries** . Performance was optimized where possible, but certain operations (especially large-scale graph computations) proved too costly in terms of time and resources.
