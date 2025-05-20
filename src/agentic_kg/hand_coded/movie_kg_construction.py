"""
This example shows how to hand-code the construction of a movie knowledge graph
by hand-coding a graph plan and then using it to construct the graph.

The goal of the agentic approach is to produce a graph plan for arbitrary input
files, not just the ones used in this example. That plan can be shared with
the user, then used to construct the graph.
"""

from agentic_kg.common.graph_plan import GraphPlan, EntityPlan, RelationPlan, Rule
from agentic_kg.common.graph_constructor import construct_graph

def add_entities(graph_plan: GraphPlan):
    # Define entity types
    movie = EntityPlan(
        name="Movie",
        description="A movie",
        property_keys=["title", "year", "plot", "rating", "genre", "director", "actors"],
    )
    actor = EntityPlan(
        name="Actor",
        description="An actor",
        property_keys=["name", "birth_date", "birth_place", "bio"],
    )
    director = EntityPlan(
        name="Director",
        description="A director",
        property_keys=["name", "birth_date", "birth_place", "bio"],
    )

    # Add entities to the graph plan
    graph_plan.add_entity(movie)
    graph_plan.add_entity(actor)
    graph_plan.add_entity(director)

    return graph_plan

def add_relations(graph_plan: GraphPlan):
    graph_plan.create_relation(
        name="ACTED_IN",
        description="An actor acted in a movie",
        from_name="Actor",
        to_name="Movie"
    )

def add_construction_rules(graph_plan: GraphPlan):
    movie = graph_plan.find_entity_by_name("Movie")
    movie.add_rule(Rule.construction(
        name="LoadMovies",
        description="Construction of the movie entity",
        tool="load_csv_nodes",
        args={
            "file_name": "movies.csv",
            "node_label": "Movie",
            "node_id_field": "movieId"
        }
    ))

    actor = graph_plan.find_entity_by_name("Actor")
    actor.add_rule(Rule.construction(
        name="LoadActors",
        description="Construction of the actor entity",
        tool="load_csv_nodes",
        args={
            "file_name": "actors.csv",
            "node_label": "Actor",
            "node_id_field": "personId"
        }
    ))

    acted_in = graph_plan.find_relation_by_name("ACTED_IN")
    acted_in.add_rule(Rule.construction(
        name="LoadActedInRelationships",
        description="Construction of the ACTED_IN relationships between Actors and Movies",
        tool="load_csv_relationships",
        args={
            "file_name": "acting_roles.csv",
            "from_label": "Actor",
            "from_id_field": "personId",
            "to_label": "Movie",
            "to_id_field": "movieId",
            "relationship_type": "ACTED_IN"
        }
    ))

if __name__ == "__main__":
    print("Planning the knowledge graph...")
    graph_plan = GraphPlan(
        name="Movie Knowledge Graph",
        description="A knowledge graph for movies and their relationships"
    )
    add_entities(graph_plan)
    add_relations(graph_plan)
    add_construction_rules(graph_plan)

    print("Constructing the knowledge graph...")
    result = construct_graph(graph_plan)
    if result["status"] == "error":
        print(result["error_message"])
        exit(1)
    
    print("Knowledge graph constructed successfully.")

    # print the graph plan
    # print(graph_plan.model_dump_json(indent=2))


