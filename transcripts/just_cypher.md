# Knowledge Graph Construction - Just Cypher

## setup

- `src/agentic_kg/agent.py` => `root_agent = just_cypher_agent()`
- `adk run src/agentic_kg`

## transcript

- user: what can you do?

- [kg_agent_v1]: I specialize in helping users create knowledge graphs. This involves understanding your specific goals, designing an appropriate graph schema, and creating the knowledge graph using tools like Cypher for Neo4j databases. I can also delegate tasks to other specialized agents, such as executing Cypher queries, to ensure the knowledge graph is built efficiently and according to your needs. If you have a project or a concept you want to model as a graph, I can assist you in bringing it to life.

- user: I am new to graphs. what are the basics?

- [kg_agent_v1]: Graphs are powerful structures used to model complex relationships and data interconnections. Here are the basics:

    ### Graph Components
    1. **Nodes (Vertices):** These are the entities in a graph. Each node represents an object, person, place, or any distinct item. For example, in a social network, nodes might represent users.

    2. **Edges (Relationships or Links):** These are the connections between nodes. They define the relationship or interaction between entities. In a social network, edges might represent the "friend" relationship between users.

    ### Types of Graphs
    1. **Directed Graphs (Digraphs):** Edges have a direction, indicating a one-way relationship (e.g., Twitter followers).

    2. **Undirected Graphs:** Edges do not have a direction, indicating a mutual relationship (e.g., Facebook friends).

    3. **Weighted Graphs:** Edges have weights, which could represent the strength, cost, or capacity of a connection (e.g., distances in a road network).

    4. **Unweighted Graphs:** Edges are equal in value, just indicating the presence of a relationship.

    ### Graph Database
    - **Property Graph Model:** A popular graph model used by databases like Neo4j. It allows nodes and edges to have properties (key/value pairs), enabling richer data representation.

    - **Cypher Query Language:** A language specifically designed to query the graph by pattern matching, similar to SQL for relational databases, but optimized for traversing relationships.

    ### Graph Operations
    - **Traversal:** Navigating through nodes and edges to search or analyze patterns, paths, or specific subgraphs.

    - **Pattern Matching:** Identifying particular patterns or connections within a graph using queries (e.g., finding mutual friends).

    ### Use Cases
    - **Social Networks:** Model connections between users.
    - **Recommendation Systems:** Recommend items by analyzing relationships (e.g., users who bought X also bought Y).
    - **Network Analysis:** Analyze complex networks like road maps, logistics, or communication networks.

    To build a knowledge graph or work with graph databases like Neo4j, you'll typically define a schema comprising nodes, relationships, properties, and leverage tools like Cypher for querying and manipulation. If you're looking into creating or querying a graph, I could help with that!

- user: create an example for me?

- [kg_agent_v1]: Absolutely! Let’s start with a simple example. 

    ### Goal:
    Let’s create a basic knowledge graph for a small library system that includes:
    - Books
    - Authors
    - Genres

    ### Graph Schema Design:
    1. **Nodes**:
    - `Book`: Represented by properties such as `title`, `published_date`
    - `Author`: Represented by properties such as `name`, `birth_date`
    - `Genre`: Represented by a property such as `name`

    2. **Relationships**:
    - `:WRITTEN_BY` relationship between `Book` and `Author`
    - `:BELONGS_TO` relationship between `Book` and `Genre`

    ### Example Data to Insert:
    - Books: "1984", "Brave New World"
    - Authors: "George Orwell", "Aldous Huxley"
    - Genres: "Dystopian", "Science Fiction"

    ### Next Steps:
    I can create this graph in your database using Cypher queries. Do you have access to a Neo4j database where you'd like to create this graph, or would you like to proceed with hypothetical data?

- user: continue

- [cypher_agent_v1]: I have created a simple knowledge graph for the library system. Here are the details of the inserted data:

    ### Nodes Created:
    1. **Authors**:
    - George Orwell (birth date: 1903-06-25)
    - Aldous Huxley (birth date: 1894-07-26)

    2. **Books**:
    - "1984" (published date: 1949-06-08)
    - "Brave New World" (published date: 1932-08-18)

    3. **Genres**:
    - Dystopian
    - Science Fiction

    ### Relationships Created:
    - "1984" is written by George Orwell and belongs to the Dystopian genre.
    - "Brave New World" is written by Aldous Huxley and belongs to the Science Fiction genre.

    ### Data Retrieved from the Graph:
    - **Book:** 1984, **Author:** George Orwell, **Genre:** Dystopian
    - **Book:** Brave New World, **Author:** Aldous Huxley, **Genre:** Science Fiction

    If you need any further modifications, queries, or additional features to explore in this graph, feel free to let me know!

- user: what kinds of queries can I run?

- [cypher_agent_v1]: You can run various types of queries in Neo4j using Cypher, depending on what information you want to retrieve, update, or analyze from the graph. Here are some examples of query types you can use:

    1. **Match Queries**: Retrieve data from the graph.
    - Example: `MATCH (b:Book) RETURN b`
    - Retrieves all books in the database.

    2. **Filter Queries**: Retrieve specific data based on conditions.
    - Example: `MATCH (a:Author) WHERE a.name = 'George Orwell' RETURN a`
    - Retrieves information about George Orwell.

    3. **Pattern Matching**: Retrieve relationships along with nodes.
    - Example: `MATCH (b:Book)-[:WRITTEN_BY]->(a:Author) RETURN b.title, a.name`
    - Retrieves book titles along with their authors.

    4. **Aggregation Queries**: Get summary information.
    - Example: `MATCH (g:Genre)<-[:BELONGS_TO]-(b:Book) RETURN g.name, count(b) as num_books`
    - Counts how many books belong to each genre.

    5. **Create Queries**: Insert new data into the graph.
    - Example: `CREATE (b:Book {title: 'New Book', published_date: '2023-01-01'})`
    - Adds a new book to the graph.

    6. **Update Queries**: Modify existing data.
    - Example: `MATCH (a:Author {name: 'Aldous Huxley'}) SET a.birth_date = '1894-07-26'`
    - Updates Huxley's birth date.

    7. **Delete Queries**: Remove data from the graph.
    - Example: `MATCH (b:Book {title: '1984'}) DELETE b`
    - Deletes the book "1984" from the graph.

    8. **Complex Queries**: Combine multiple operations.
    - Example: `MATCH (b:Book)-[:WRITTEN_BY]->(a:Author) DELETE b, a`
    - Deletes books along with their authors.

    If you have a specific query or type of information you're interested in, feel free to ask, and I can help you construct the appropriate Cypher query!

- user: How many authors are in the library?

- [cypher_agent_v1]: There are **2 authors** in the library. If you have any more questions or need additional queries, just let me know!

- user: How did you do that?

- [cypher_agent_v1]: I executed a Cypher query against the Neo4j database to count the number of authors. Here's a breakdown of the process:

    1. **MATCH Clause**: This part of the query specifies that we want to find nodes with the label `Author`.
    - `MATCH (a:Author)`

    2. **RETURN Clause**: This part of the query specifies what we want to return from our match. In this case, I used the `count()` function to get the total number of authors found.
    - `RETURN count(a) AS num_authors`

    3. **Execution**: I submitted this query to the Neo4j database, and it returned the result, which indicated there are 2 authors.

    If you have specific queries you'd like to construct or any other questions, feel free to ask!

- user: reset the database

- [cypher_agent_v1]: The database has been successfully reset. All data, indexes, and constraints have been removed. If you need to recreate any data or have further actions to perform, just let me know!

- user: show the database schema

- [cypher_agent_v1]: The database schema is currently empty. Here are the details:

    - **Node Properties**: None
    - **Relationship Properties**: None
    - **Relationships**: None
    - **Constraints**: None
    - **Indexes**: None

    Since the database has been reset, there are no nodes, relationships, or any schema elements present. If you'd like to add data and see how the schema develops, let me know!

- user: recreate the library example

- [cypher_agent_v1]: The library example has been successfully recreated in the database. Here are the details of the inserted data:

    ### Nodes Created:
    1. **Authors**:
    - George Orwell (birth date: 1903-06-25)
    - Aldous Huxley (birth date: 1894-07-26)

    2. **Books**:
    - "1984" (published date: 1949-06-08)
    - "Brave New World" (published date: 1932-08-18)

    3. **Genres**:
    - Dystopian
    - Science Fiction

    ### Relationships Created:
    - "1984" is written by George Orwell and belongs to the Dystopian genre.
    - "Brave New World" is written by Aldous Huxley and belongs to the Science Fiction genre.

    ### Data Retrieved from the Graph:
    - **Book:** 1984, **Author:** George Orwell, **Genre:** Dystopian
    - **Book:** Brave New World, **Author:** Aldous Huxley, **Genre:** Science Fiction

    If you have any further questions or need anything else, feel free to ask!

- user: list the authors

- [cypher_agent_v1]: Here are the authors in the library:

    1. George Orwell
    2. Aldous Huxley

    If you need more information or additional queries, just let me know!

- user: show the schema

- [cypher_agent_v1]: Here is the current schema of the database:

    ### Node Properties:
    1. **Author**:
    - `name`: STRING
    - `birth_date`: STRING

    2. **Book**:
    - `title`: STRING
    - `published_date`: STRING

    3. **Genre**:
    - `name`: STRING

    ### Relationships:
    1. **WRITTEN_BY**:
    - Start: `Book`
    - End: `Author`

    2. **BELONGS_TO**:
    - Start: `Book`
    - End: `Genre`

    ### Constraints and Indexes:
    - No constraints found.
    - No indexes found.

    If you need more information or further assistance, feel free to ask!

- user: can you create a graph from csv files?

- [kg_agent_v1]: To create a graph from CSV files, I’d need to first ensure the CSV files are prepared and placed in the Neo4j import directory. However, I do not have the ability to directly access or handle files.

    If you can provide the CSV files, you can manually load them into Neo4j using the `LOAD CSV` command as I previously outlined.

    If you're familiar with your Neo4j instance and the import directory, you can proceed to upload those CSV files and then execute the provided Cypher commands.

    If you need assistance in loading the data or executing the commands, please let me know!


## Review

- ok, pretty good! a graph from thin air with great explanations
- next up, let's try to constuct a graph from source data files
