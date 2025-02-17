# Spatial Relationships Detection Report

## Overview

A command-line interface (CLI) tool was developed to analyze various spatial relationships between different geographical features. The tool provides a unified interface to execute pre-determined spatial analyses through simple numeric commands.

## CLI Tool Details

The tool is implemented as a Python script that accepts a single numeric parameter (1-10) corresponding to different analyses. Key features include:

- Simple command-line execution: `python cli_tool_rel.py <number>`
- Automatic execution time measurement for performance monitoring
- Error handling for script execution and data processing
- Consistent output format across different analyses

Example usage:

```bash
python cli_tool_rel.py 1  # Execute cities-communes analysis
python cli_tool_rel.py 7  # Execute nearby trees analysis
```

## Implementation Highlights

### 1. Cities within Communes

Implementation:

- Data loaded from `cities` and `communes` collections
- Spatial join using `gpd.sjoin()` with 'within' predicate
- Output: matched pairs of city and commune IDs
- About ~25000 records, ~3 min

### 2. Communes within Powiats

Similar implementation to task 1:

- Data from `communes` and `powiats` collections
- Spatial join with 'within' predicate
- Returns commune-powiat ID pairs
- About 1600 records, ~1 min

### 3. Powiats within Voivodships

Follows the same pattern:

- Uses `powiats` and `voivodships` collections
- Spatial join (within)
- Outputs powiat-voivodship relationships
- About 400 records, ~30 sec

### 4. Voivodships within Countries

Implementation matches previous tasks:

- Data from `voivodships` and `countries` collections
- Spatial join for containment analysis
- Returns voivodship-country pairs
- 18 records, ~10 sec

### 5. Neighboring Communes

Different approach:

- Data loaded from `communes` collection only
- Self-join using `gpd.sjoin()` with 'intersects' predicate
- Returns pairs of adjacent commune IDs
- About 6000 records, ~30 sec

### 6. Buildings collections

- Similar to trees
- Implements `scipy.spatial.cKDTree` for efficient distance queries
- Extracts x,y coordinates for KD-tree
- `query_pairs()` finds all pairs within 500m
- Limited to 100_000 buildings ~ around 8 minutes


### 7. Nearby Trees (≤50m)

More complex implementation:

- Uses `trees` collection
- Coordinate conversion to metric system
- Implements `scipy.spatial.cKDTree` for efficient distance queries
- Extracts x,y coordinates for KD-tree
- `query_pairs()` finds all pairs within 50m
- Returns tree ID pairs and distances
- Around 8 milion records,  ~1,5 min

### 8. Trees Near Roads (≤20m)

Similar to task 7:

- Uses `trees` and `roads` collections
- Coordinate conversion to metric system
- Buffer or distance-based query
- Returns tree-road pairs within 20m
- Around 3/4 of milion, 10-15 min execution

### 9. Road Connectivity

Network analysis:

- Analyzes road endpoints and nodes
- Identifies intersection points
- Classifies connection types (start/mid/end)
- Returns connected road pairs with node info

### 10. Railway-Road Intersections

Geometric analysis:

- Data from `railways` and `roads` collections
- Finds intersection points
- Calculates angles between intersecting segments
- Returns railway-road pairs with intersection angles
- Close to 80,000 records, ~15-25 min

### Table with exact times (with adding edges to the database):
 - Relation 1: 112.21s
 - Relation 2: 50.28s
 - Relation 3: 20.49s
 - Relation 4: 7.83s
 - Relation 5: 23.41s
 - Relation 6: 676.43s (for 100000 buildings)
 - Relation 7: 813.46s 
 - Relation 8: 1878.11s
 - Relation 9: 2203.87s
 - Relation 10: 90.78s

## Technical implementation

### Spatial Processing

- Utilizes GeoPandas for spatial operations
- Implements spatial joins for boundary relationships
- Uses KD-tree spatial indexing for efficient distance queries
- Employs proper coordinate transformations for accurate measurements

### Database Integration

- Connects to ArangoDB for data retrieval
- Handles GeoJSON to Shapely geometry conversions
- Ensures proper spatial reference system handling
- Maintains data integrity throughout processing

### Performance Considerations

- Implements efficient spatial indexing where appropriate
- Uses vectorized operations where possible
- Includes progress monitoring for long-running operations
- Optimizes memory usage for large datasets
