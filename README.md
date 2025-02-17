## **Final report**

### **Technology choice**

- Arango DB (noSQL database which combines relational and non-relational databases)
- Geopandas (tool for manipulating spatial data)
- Networkx (python library to create and exploit graphs)


### **Prerequisites**

- docker compose installed
- python at least 3.10

### **System architecture

1. Data stored in ArangoDB collection (imported with main2.py file in app folder)
2. Relationships detected by CLI tool or python files. All in app/relations/
3. Queries being made with help of AQL and basic pandas processing. All in app/queries_2.0

### **Deployment instructions**

To deploy pull the repo than go into the folder and type:
```
docker-compose up --build
```

To run a certain file just do:
```
docker exec -it python-app python /app/file_name.py
```

app/main_v2.py - initializing database
app/queries_2.0/cli_tool_queries.py - queries tool
app/rel/cli_tool_rel.py - relationship tool

*After queries and rel tool specify a number of query or relationship

### **Manuals for all tools provided**

How to use CLI tools:

- Just type:
```
python cli_tool_rel.py {insert here number from 1 to 10}
```

And the consequent relation will execute and give you the execution time.

Do the same with cli_tool_query

To change the paramters of queries, change them in the corresponding python files.

### **Timeline of design and development**

16.12 - Database import implemented
9.01 - Relationship implemented
23.01 - Queries implemented
26.01 - Revised queries implemented

### **Division of tasks among project members**

Jan Tyc -> Data import, Queries
Bartłomiej Tarcholik -> Data model, Relationship detection

### Exact data considering solutions 

More data about solutions and critical analysis can be found in reports:
- report_data_import.md
- report_relations.md
- report_queries.md

About the specifics of each milestone encountered



