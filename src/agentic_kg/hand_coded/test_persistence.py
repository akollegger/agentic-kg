#!/usr/bin/env python
"""
Test script to verify the persistence functions for GraphPlan.
"""

from agentic_kg.common.graph_plan import GraphPlan, EntityPlan, RelationPlan, Rule, RuleKind, FileSource
from agentic_kg.common.graph_plan import store_graph_plan, retrieve_graph_plan

def create_test_graph_plan():
    """Create a test graph plan with entities, relations, and rules."""
    graph_plan_id = "test_persistence_plan"
    graph_plan = GraphPlan(
        id=graph_plan_id,
        name="Test Persistence Plan",
        description="A test plan for verifying persistence functions"
    )
    
    # Add a file source
    source = FileSource(
        file_path="test_data.csv",
        mime_type="text/csv",
        header=["id", "name", "description"]
    )
    graph_plan.sources[source.file_path] = source
    
    # Add entities
    person = EntityPlan(
        name="Person",
        description="A person entity",
        property_keys=["name", "age", "email"]
    )
    
    # Add a construction rule to the person entity
    person_rule = Rule(
        kind=RuleKind.CONSTRUCTION,
        tool="csv_loader",
        args={
            "file_path": "people.csv",
            "id_field": "id"
        }
    )
    person.rules.append(person_rule)
    
    # Add a retrieval rule to the person entity
    person_retrieval = Rule(
        kind=RuleKind.RETRIEVAL,
        tool="cypher_query",
        args={
            "query": "MATCH (p:Person) RETURN p"
        }
    )
    person.rules.append(person_retrieval)
    
    # Add the person entity to the graph plan
    graph_plan.add_entity(person)
    
    # Add another entity
    product = EntityPlan(
        name="Product",
        description="A product entity",
        property_keys=["name", "price", "category"]
    )
    graph_plan.add_entity(product)
    
    # Add a relation between person and product
    purchased = RelationPlan(
        name="PURCHASED",
        description="A person purchased a product",
        from_entity=person,
        to_entity=product,
        property_keys=["date", "quantity", "price"]
    )
    
    # Add a construction rule to the relation
    purchased_rule = Rule(
        kind=RuleKind.CONSTRUCTION,
        tool="csv_relation_loader",
        args={
            "file_path": "purchases.csv",
            "from_field": "person_id",
            "to_field": "product_id"
        }
    )
    purchased.rules.append(purchased_rule)
    
    # Add the relation to the graph plan
    graph_plan.add_relation(purchased)
    
    return graph_plan

def test_persistence():
    """Test storing and retrieving a graph plan."""
    # Create a test graph plan
    graph_plan = create_test_graph_plan()
    graph_plan_id = graph_plan.id
    
    # Store the graph plan
    print(f"Storing graph plan with ID: {graph_plan_id}")
    store_graph_plan(graph_plan)
    
    # Retrieve the graph plan
    print(f"Retrieving graph plan with ID: {graph_plan_id}")
    retrieved_plan = retrieve_graph_plan(graph_plan_id)
    
    # Verify the retrieved plan
    if retrieved_plan:
        print("Successfully retrieved graph plan:")
        print(f"  ID: {retrieved_plan.id}")
        print(f"  Name: {retrieved_plan.name}")
        print(f"  Description: {retrieved_plan.description}")
        print(f"  Entities: {len(retrieved_plan.entities)}")
        for entity_id, entity in retrieved_plan.entities.items():
            print(f"    - {entity.name}: {len(entity.rules)} rules")
            for rule in entity.rules:
                print(f"      * {rule.kind.name} rule using {rule.tool}")
        print(f"  Relations: {len(retrieved_plan.relations)}")
        for relation_id, relation in retrieved_plan.relations.items():
            print(f"    - {relation.name}: {len(relation.rules)} rules")
            for rule in relation.rules:
                print(f"      * {rule.kind.name} rule using {rule.tool}")
        print(f"  Sources: {len(retrieved_plan.sources)}")
        for path, source in retrieved_plan.sources.items():
            print(f"    - {path}: {source.mime_type}")
    else:
        print(f"Failed to retrieve graph plan with ID: {graph_plan_id}")

if __name__ == "__main__":
    test_persistence()
