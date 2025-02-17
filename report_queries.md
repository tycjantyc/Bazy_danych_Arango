# Queries Report

## Overview

A command-line interface (CLI) tool was developed to analyze various spatial relationships between different geographical features. The tool provides a unified interface to execute pre-determined spatial analyses through simple numeric commands.

## CLI Tool Details

The tool is implemented as a Python script that accepts a single numeric parameter (1-10) corresponding to different analyses. Key features include:

- Simple command-line execution: `python cli_tool_queries.py <number>`
- Automatic execution time measurement for performance monitoring
- Error handling for script execution and data processing
- Consistent output format across different analyses

Example usage:

```bash
python cli_tool_queries.py 1  # Execute cities-communes analysis
python cli_tool_queries.py 7  # Execute tree clusters analysis
```

## Implementation Highlights

### 1. Number of cities within Communes

```
FOR commune IN communes
    LET cityCount = LENGTH(
        FOR city IN INBOUND commune edges_rel_1
            FILTER IS_SAME_COLLECTION('cities', city)
            RETURN city
    )
    RETURN { commune: commune.name, cityCount: cityCount }
```

- predicate 'INBOUND'
- JSON output format
- Execution time: 10 s.

### 2. Adjacent powiats

```
FOR powiat IN powiats
    LET adjacentPowiats = UNIQUE(
        FOR commune IN INBOUND powiat edges_rel_2 // Traverse powiat → its communes
            FOR neighborCommune IN OUTBOUND commune edges_rel_5 // Traverse commune → adjacent communes
                FOR neighborPowiat IN OUTBOUND neighborCommune edges_rel_2 // Adjacent commune → its powiat
                    FILTER IS_SAME_COLLECTION('powiats', neighborPowiat) AND neighborPowiat._id != powiat._id
                    RETURN neighborPowiat.name
    )
    RETURN { powiat: powiat.name, adjacentPowiats: adjacentPowiats }
```


- JSON output format
- Execution time: 23 s.

### 3. Adjacent voivodships

```
FOR voivodship IN voivodships
    LET adjacentVoivodships = UNIQUE(
        FOR powiat IN INBOUND voivodship edges_rel_3 
            FOR commune IN INBOUND powiat edges_rel_2 
                FOR neighborCommune IN OUTBOUND commune edges_rel_5 
                    FOR neighborPowiat IN OUTBOUND neighborCommune edges_rel_2 
                        FOR neighborVoivodship IN OUTBOUND neighborPowiat edges_rel_3 
                            FILTER IS_SAME_COLLECTION('voivodships', neighborVoivodship) AND neighborVoivodship._id != voivodship._id
                            RETURN neighborVoivodship.name
    )
    RETURN { voivodship: voivodship.name, adjacentVoivodships: adjacentVoivodships }

```

- Use of geopandas sjoin
- predicate 'intersects'
- JSON output format
- Execution time: 90 s.

### 4. Clusters of buildings; parameters

- Usage of relationship 6
- Creates graph with networkx
- JSON output format
- Execution time (for 100_000 buildings): 34s

### 5. Road/railway crossings

```
query = f"FOR crossing IN edges_rel_10 FILTER crossing.angle >= {min_angle} AND crossing.angle <= {max_angle} RETURN {{road: crossing._from,railway: crossing._to,angle: crossing.angle}}"
```

- Useage of relation 10
- check the min max angle
- JSON output format
- Execution time: 10 s.

### 6. Roads which run parallel to railways

- Custom sjoin function
- Parameters: maxdistance (between road and railway) and max angle (pallarel to 1 degree of 0.5 degree)
- JSON output format
- Execution time: 17 minutes

### 7. Clusters of trees

```
FOR edge IN {edges_name}
        FILTER edge.distance < {max_distance}
        LET left_tree = DOCUMENT("trees", edge.id_left)
        LET right_tree = DOCUMENT("trees", edge.id_right)
        RETURN {{
            id_f: edge.id_left,
            id_t: edge.id_right,
            distance: edge.distance,
            geom_f: left_tree.geometry,
            geom_t: right_tree.geometry
        }}
```

- Parameters: maxdistance - eps, min samples
- JSON output format
- Execution time: 16 mins.


### 10. Roads with trees near them

```
FOR edge IN {edges_name}
        LET left_tree = DOCUMENT("trees", edge.id_left)
        LET right_tree = DOCUMENT("roads", edge.id_right)
        RETURN {{
            id_f: edge.id_left,
            id_t: edge.id_right,
            geom_f: left_tree.geometry,
            geom_t: right_tree.geometry
        }}
```

- Creater buffer within road and counts trees within it
- Filters those with not sufficient number
- JSON output format
- Execution time: About 90s.

# Overview

| Lp. | Done? | Time       |
| --- | ----- | ---------- |
| 1   | +     | 10s        |
| 2   | +     | 23s        |
| 3   | +     | 70s        |
| 4   | -     | -          |
| 5   | +     | 10s        |
| 6   | +     | 17min      |
| 7   | +     | 90s        |
| 8   | -     | -          |
| 9   | -     | -          |
| 10  | +     | 64s        |
