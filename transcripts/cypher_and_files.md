# Knowledge Graph Construction - Cypher and Files

## setup

- `src/agentic_kg/agent.py` => `root_agent = cypher_and_files_agent()`
- `data/movies/some/*`
- `adk run src/agentic_kg`

## transcript

- user: what can you do?

- [kg_agent_v2]: I can help you create a knowledge graph from your data sources by following these steps:

    1. **Analyze Data Sources**: I can evaluate your data to identify relationships, redundancies, and overall structure.
    
    2. **Design Graph Schema**: I can propose a physical graph schema that fits your available data and aligns with your goals, including defining nodes, relationships, properties, and any necessary indexes or constraints.

    3. **Prepare Data for Import**: I can assist in making sure that your data is ready for import by managing file operations and preparing the necessary metadata.

    4. **Import Data**: I can execute the import of your data into a graph database using Cypher queries.

    Through collaboration with specialized sub-agents, I can manage file operations and execute Cypher queries efficiently. Let me know how you'd like to proceed or if you have any specific data sources in mind!

- user: what data is available?

- [dataprep_agent_v1]: Here are the files available in the data directory that have gone through data preparation:

    1. **Movie Fans:**
    - movie_fans_us.csv
    - movie_fans.csv

    2. **Movie Reviews:**
    - movie_reviews_us.csv
    - fan_reviews_us.csv

    3. **Movies:**
    - people.csv
    - acting_roles.csv
    - movies.csv

    4. **Social Reviews:**
    - A variety of reviews with different filenames, such as:
        - valentines_day_WN9p.md
        - sucker_punch_e2VA.md
        - the_book_of_eli_BZTY.md
        - many others...

    Additionally, I attempted to list the files available in the Neo4j import directory, but encountered an error: **"Neo4j import directory not yet known."** 

    Would you like me to assist you further with any specific files or tasks?

- user: where is Neo4j configured to look for import data?

- [cypher_agent_v1]: Neo4j is configured to look for import data in the following directory:

    `/Users/akollegger/Library/Application Support/com.Neo4j.Relate/Data/dbmss/dbms-987f0555-5d26-43c0-a553-8db6b01bec19/import`

- user: list the files in the import directory

- [dataprep_agent_v1]: The import directory is currently empty; there are no files available for import to Neo4j. If you would like to upload files or need assistance with anything else, feel free to ask!

- user: tell me more about the some_*.csv files that have been prepared

- [dataprep_agent_v1]: Here are the details about the `some_*.csv` files:

    1. **File: `some_actors_with_bios.csv`**
    - **Type:** CSV
    - **Sample Data:**
        | personId | name           | birthYear | deathYear | bio                                                                                                                                                                                                |
        |----------|----------------|-----------|-----------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
        | 2        | Mark Hamill    | 1951      |           | Fiction: Mark Hamill, the legendary space wizard... convinced they're the next big trend in woodland fashion.                                                                                     |
        | 3        | Harrison Ford  | 1942      |           | Fiction: Harrison Ford... leading to local wildlife disputes that are still the stuff of legend.                                                                                                   |
        | 31       | Tom Hanks      | 1956      |           | Fiction: Tom Hanks once tried to establish himself as a professional dog whisperer... prompting their eventual revolt against the tyranny of the toy box.                                           |
        | 35       | Sally Field    | 1946      |           | Fiction: Sally Field... attempting to decipher the secret language of squirrels.                                                                                                                   |

    2. **File: `some_movies_with_plots.csv`**
    - **Type:** CSV
    - **Sample Data:**
        | movieId | title                                       | avgVote | releaseYear | genres                              | plot                                                                                                                                                         |
        |---------|---------------------------------------------|---------|-------------|-------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
        | 189     | Sin City: A Dame to Kill For                | 6.9     | 2014        | Action: Crime: Drama: Thriller      | In a gritty and corrupt city, a hard-boiled private detective navigates a web of deception and double-crosses as he seeks vengeance and redemption.               |
        | 1771    | Captain America: The First Avenger          | 6.3     | 2011        | Action: Adventure: Science Fiction  | In a world on the brink of war, a frail young man transforms into a super-soldier to combat a ruthless villain and protect humanity.                             |
        | 1865    | Pirates of the Caribbean: On Stranger Tides | 6.3     | 2011        | Action: Adventure: Fantasy          | In a thrilling quest across treacherous seas, a notorious captain embarks on a daring expedition to find the fabled Fountain of Youth.                         |
        | 1930    | The Amazing Spider-Man                      | 6.3     | 2012        | Action: Adventure: Fantasy          | In a thrilling battle against personal and external demons, a young man discovers his extraordinary powers and must navigate the challenges of love and responsibility. |

    3. **File: `some_acting_roles.csv`**
    - **Type:** CSV
    - **Sample Data:**
        | personId | movieId | characters |
        |----------|---------|------------|
        | 2295     | 189     | Marv       |
        | 56731    | 189     | Nancy      |
        | 16851    | 189     | Dwight     |
        | 24045    | 189     | Johnny     |

    If you need more information or wish to perform any actions with these files, feel free to ask!

- user: construct a graph from those some_*.csv files

- [kg_agent_v2]: To construct a graph from the `some_*.csv` files, we’ll follow these steps:

    1. **Analyze the Data Sources:**
    - The `some_actors_with_bios.csv` contains information about actors with their details.
    - The `some_movies_with_plots.csv` includes movie titles, genres, and plot summaries.
    - The `some_acting_roles.csv` establishes relationships by linking actors to the specific characters they portrayed in different movies.

    2. **Design the Graph Schema:**
    - **Nodes:**
        - **Actors:** Will contain properties like `personId`, `name`, `birthYear`, `deathYear`, `bio`.
        - **Movies:** Will contain properties like `movieId`, `title`, `avgVote`, `releaseYear`, `genres`, `plot`.
    - **Relationships:**
        - **ACTED_IN:** Between Actors and Movies, indicating the role they played in that movie, with `characters` as a property.

    3. **Prepare Data for Import:**
    - Ensure the `some_*.csv` files are accessible for import into Neo4j.

    4. **Perform the Import:**
    - Load data from the CSV files into the Neo4j database to create the nodes and relationships as defined.

    Let’s start by ensuring the data files are available in the Neo4j import directory so that we can proceed with the import. Checking the import directory settings first.

- [cypher_agent_v1]: The graph has been successfully constructed from the `some_*.csv` files in Neo4j. Here’s a summary of what has been achieved:

    1. **Actors Nodes:**
    - Each actor from `some_actors_with_bios.csv` has been created as a node with properties such as `personId`, `name`, `birthYear`, `deathYear`, and `bio`.

    2. **Movies Nodes:**
    - Each movie from `some_movies_with_plots.csv` has been created as a node with properties such as `movieId`, `title`, `avgVote`, `releaseYear`, `genres`, and `plot`.

    3. **ACTED_IN Relationships:**
    - Relationships have been established from the `some_acting_roles.csv`, linking actors to the movies they acted in along with the character names they portrayed.

    If you need further analysis or would like to query the constructed graph, just let me know!

- user: what are some questions that can be answered with this graph?

- [cypher_agent_v1]: With the constructed graph from the `some_*.csv` files, you can answer a variety of questions, including:

    1. **Actor Information:**
    - What are the birth and death years of a specific actor?
    - What bio information is available for a specific actor?
    - How many movies has a specific actor acted in?

    2. **Movie Information:**
    - What are the details (title, genres, plot) of a specific movie?
    - What is the average rating of a specific movie?
    - What movies were released in a particular year or genre?

    3. **Relationships:**
    - Who acted in a specific movie?
    - What characters did a particular actor portray in their filmography?
    - Which actors have collaborated on multiple movies together?

    4. **Analysis of Trends:**
    - Which genres are most common among the movies in the graph?
    - How do average ratings vary across different genres?
    - Are there any notable trends in actor birth years or movie release years?

    5. **Connections:**
    - Find actors who have portrayed characters in the same movie.
    - Explore the connections between actors and movies to see patterns in their careers.

    These questions can help you gain insights into actors, movies, and their relationships within your data. If you have specific queries in mind, I can assist you in formulating the Cypher queries to retrieve that information!

- user: Which movie has the most actors?     

- [cypher_agent_v1]: The movie with the most actors is **"Harry Potter and the Deathly Hallows: Part 1"**, which has a total of **55 actors** associated with it. If you have any other questions or need further analysis, feel free to ask!

- user: show your work

- [cypher_agent_v1]: To find the movie with the most actors in the graph, I executed the following Cypher query:

    ```cypher
    MATCH (a:Actor)-[:ACTED_IN]->(m:Movie) 
    RETURN m.title AS Movie, COUNT(a) AS ActorCount 
    ORDER BY ActorCount DESC 
    LIMIT 1
    ```

    ### Explanation of the Query:
    1. **MATCH (a:Actor)-[:ACTED_IN]->(m:Movie)**: This part of the query finds all actors (`a`) and the movies (`m`) they have acted in by following the `ACTED_IN` relationships.

    2. **RETURN m.title AS Movie, COUNT(a) AS ActorCount**: This returns two values:
    - The title of the movie.
    - The count of actors associated with each movie.

    3. **ORDER BY ActorCount DESC**: This arranges the results in descending order based on the count of actors. The movie with the highest number of actors will be at the top.

    4. **LIMIT 1**: This limits the result to only the top movie that has the most actors.

    The result of this query revealed that "Harry Potter and the Deathly Hallows: Part 1" has the highest number of actors, specifically 55 actors.

    If you need further insights or additional queries, just let me know!

- user: What enhancements can we make to this graph? 

- [cypher_agent_v1]: To enhance the current graph built from the `some_*.csv` files, several improvements could be considered:

    1. **Additional Node Types:**
    - **Directors:** Include a `Director` node to store information about movie directors, along with relationships indicating which movies they directed.
    - **Genres:** Create `Genre` nodes to allow for more detailed relationships and categorization. This would enable more complex genre relationships (e.g., a movie could belong to multiple genres).

    2. **Properties and Attributes:**
    - **More Movie Attributes:** Add properties like budget, box office gross, and runtime to the `Movie` nodes to provide more context and enable deeper analysis.
    - **Detailed Actor Attributes:** Include additional attributes for actors, such as nationality, awards won, and social media links.

    3. **Relationships and Edges:**
    - **Collaborations:** Establish relationships to indicate collaborations between actors on different movies, allowing for queries about frequent co-stars.
    - **Awards:** Create relationships to represent awards won by actors or movies. This could include nodes for specific awards (e.g., Oscars) and relationships indicating nominations or wins.

    4. **Temporal Data:**
    - **Temporal Relationships:** Introduce time-based relationships or nodes (e.g., periods, decades) to allow for historical analyses, trends over time, or generational comparisons.

    5. **Ratings and Reviews:**
    - **User Ratings and Reviews:** Create nodes for users who interact with movies, allowing users to rate or review movies and enabling recommendations based on ratings.

    6. **Visual Improvements:**
    - **Graph Visualization Enhancements:** Use graph visualization tools to create more informative representations of the graph, allowing users to explore relationships visually.

    7. **Export Features:**
    - **CSV Export:** Allow exporting of certain nodes or relationships back to CSV format, making it easier to share or analyze data outside of Neo4j.

    8. **Recommendations and Insights:**
    - Develop algorithms to provide insights or recommendations using techniques such as collaborative filtering based on actor movie choices or genre preferences.

    By implementing these enhancements, the graph could become a more comprehensive and valuable resource for querying and analyzing relationships in the entertainment domain. If you're interested in adding specific enhancements, I can assist with formulating the necessary Cypher queries!

- user: I'm now curious about the personal interests, history and acting for actors. How could we enhance the graph to improve that analysis?

- [cypher_agent_v1]: To enhance the graph and improve the analysis of actors' personal interests, history, and acting careers, consider the following strategies:

    1. **Actors' Personal Interests:**
    - **Interests Node:** Create a new node type (e.g., `Interest`) representing various personal interests (e.g., hobbies, causes, etc.) and establish a relationship between `Actor` nodes and their corresponding `Interest` nodes.
    - **Favorite Genres:** Include properties or relationships to capture actors’ favorite movie genres or types of roles they prefer.

    2. **Career History:**
    - **Career Timeline:** Implement a timeline node or use properties in the `Actor` node itself to document significant career milestones (e.g., notable roles, awards, career changes).
    - **Filmography Node:** Create a `Filmography` node that could aggregate and provide insights about significant developments in an actor's career, linking them to images, media, and major productions throughout their career.

    3. **Collaborations:**
    - **Collaboration Nodes:** Establish a collaboration node that could encompass various working relationships between actors (e.g., frequent co-stars), directors, and writers. This could provide insights into an actor’s collaborative history.
    - **Teams:** Group actors who frequently work together into an `Ensemble` node, allowing for easier queries about collaborative works.

    4. **Awards and Recognitions:**
    - **Awards Node:** Create nodes for various awards (e.g., Oscars, Golden Globes) that can store details about the award type, year, and category. Link actors to these nodes through relationships that indicate nominations and wins.
    - **Milestones:** Use additional properties in Actor nodes for tracking major career milestones, such as first acting role or significant career changes.

    5. **Biographical Details:**
    - **Expanded Biographical Node:** Include more detailed nodes or relationship properties that capture the actor's background, family, upbringing, education, and notable life events.
    - **Spouses and Family Members:** Connect actors to their spouses or family members if they are also notable figures in the industry or if their relationships significantly influence their careers.

- user: perhaps "enhance" is the wrong word. could we enrich the Actor nodes to make it easier to find out about their personal interests?

- [cypher_agent_v1]: Yes, enriching the Actor nodes with additional properties and relationships can make it easier to analyze their personal interests. Here are specific suggestions for enriching the Actor nodes:

    1. **Add Properties for Personal Interests:**
    - **Interests List:** Add a property such as `interests`, which could be a list or array capturing various hobbies, passions, or interests (e.g., ["photography", "cooking", "environmental activism"]).
    - **Favorite Genres:** Include a property such as `favoriteGenres` to store the actor's preferred movie genres.
    - **Known Causes:** Another property like `knownCauses` can be used to represent social causes the actor is passionate about (e.g., ["animal rights", "education reform"]).

    2. **Create Relationships with Interests Nodes:**
    - **Interest Nodes:** Create individual nodes representing different interests or causes. For example, nodes for specific hobbies, and establish relationships (`HAS_INTEREST`) between the Actor nodes and these Interest nodes.
    - **Frequent Collaborators:** Add relationships to represent frequent collaborators, indicating personal affinities or shared projects with other actors, directors, or writers.

    3. **Background Information:**
    - **Bio Property Expansion:** Enrich the `bio` property to include more personal anecdotes or interests that influence their acting careers.
    - **Milestones:** Include properties to highlight educational background, significant personal achievements, or life experiences that shaped their career (e.g., `education`, `notableExperiences`).

    4. **Social Media Links:**
    - **Social Links Property:** Add properties for various social media handles or personal websites, such as `twitterHandle`, `instagramHandle`, or `personalWebsite`, to facilitate understanding of their public persona and interests.

    5. **Quotes and Reflections:**
    - **Quotes Property:** Add a property for notable quotes or statements they have made reflecting their interests or philosophy (e.g., `inspirationalQuote`).

    By implementing these enrichments directly in the Actor nodes, you can make it much easier to query and analyze personal interests and background information about the actors. This would also allow for more engaging presentations or storytelling around their characters and roles in films.

    If you would like assistance with how to implement these changes in your graph, including the specific Cypher queries for updating the Actor nodes, let me know!

- user: again, that's not quite what I mean. the actor bios already contain some information about their background and interests. how can we make it easier to search that?

- [cypher_agent_v1]: To make it easier to search through the existing actor bios and extract information about their backgrounds and interests, you can implement the following enhancements:

    1. **Full-Text Search Indexing:**
    - **Create a Full-Text Index:** Use Neo4j’s full-text search capabilities to create an index on the `bio` property of the Actor nodes. This allows you to perform more efficient text searches within the bios.
    - **Example Query to Create an Index:**
        ```cypher
        CALL db.index.fulltext.createNodeIndex("ActorBioIndex", ["Actor"], ["bio"])
        ```

    2. **Text Analysis and Tagging:**
    - **Keyword Extraction:** Analyze the existing bios to extract relevant keywords and phrases, and store these in an additional property (e.g., `keywords` as a list). This could involve using NLP (Natural Language Processing) tools externally and then populating the graph with the extracted keywords.
    - **Example Update Query:**
        ```cypher
        MATCH (a:Actor)
        SET a.keywords = ['actor', 'space wizard', 'knitter'] // Example keywords
        ```

    3. **Search Queries for Bios:**
    - **Text Search Queries:** Use full-text search capabilities to query through the bios efficiently. For example, you could search for specific interests or background information directly.
    - **Example Search Query:**
        ```cypher
        CALL db.index.fulltext.queryNodes("ActorBioIndex", "knitting") YIELD node 
        RETURN node.name, node.bio
        ```


## Review

- the Agent needed a lot of coaxing to consider adding an index. this is an important part of data modeling. let's work on that
- add some explicit tools for creating indexes, along with better prompting for considering how to enhance the graph data to improve retrieval
