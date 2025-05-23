"""
Unit tests for the graph_plan module.
"""

import pytest
from pydantic import ValidationError

from ..graph_plan import GraphPlan, EntityPlan, RelationPlan, Rule, RuleKind, FileSource


class TestGraphPlan:
    """Tests for the GraphPlan class and related components."""

    def test_create_graph_plan(self):
        """Test creating a basic graph plan."""
        graph_plan = GraphPlan(
            name="Test Graph Plan",
            description="A test graph plan"
        )
        
        assert graph_plan.id is not None
        assert graph_plan.name == "Test Graph Plan"
        assert graph_plan.description == "A test graph plan"
        assert len(graph_plan.entities) == 0
        assert len(graph_plan.relations) == 0
        assert len(graph_plan.sources) == 0

    def test_add_entity(self):
        """Test adding an entity to a graph plan."""
        graph_plan = GraphPlan(
            name="Test Graph Plan",
            description="A test graph plan"
        )
        
        entity = EntityPlan(
            name="Person",
            description="A person entity"
        )
        
        graph_plan.add_entity(entity)
        
        assert len(graph_plan.entities) == 1
        assert entity.id in graph_plan.entities
        assert graph_plan.entities[entity.id] == entity
        
        # Test retrieving by name
        retrieved_entity = graph_plan.find_entity_by_name("Person")
        assert retrieved_entity == entity
        
        # Test retrieving by ID
        retrieved_entity = graph_plan.get_entity_by_id(entity.id)
        assert retrieved_entity == entity

    def test_add_relation(self):
        """Test adding a relation between entities."""
        graph_plan = GraphPlan(
            name="Test Graph Plan",
            description="A test graph plan"
        )
        
        person = EntityPlan(
            name="Person",
            description="A person entity"
        )
        
        organization = EntityPlan(
            name="Organization",
            description="An organization entity"
        )
        
        graph_plan.add_entity(person)
        graph_plan.add_entity(organization)
        
        works_for = RelationPlan(
            name="WORKS_FOR",
            description="Person works for an organization",
            from_entity=person,
            to_entity=organization
        )
        
        graph_plan.add_relation(works_for)
        
        assert len(graph_plan.relations) == 1
        assert works_for.id in graph_plan.relations
        assert graph_plan.relations[works_for.id] == works_for
        
        # Test retrieving relations for an entity
        person_relations = graph_plan.get_relations_for_entity(person)
        assert len(person_relations) == 1
        assert person_relations[0] == works_for
        
        org_relations = graph_plan.get_relations_for_entity(organization)
        assert len(org_relations) == 1
        assert org_relations[0] == works_for

    def test_add_rule(self):
        """Test adding rules to graph plan elements."""
        graph_plan = GraphPlan(
            name="Test Graph Plan",
            description="A test graph plan"
        )
        
        person = EntityPlan(
            name="Person",
            description="A person entity"
        )
        
        graph_plan.add_entity(person)
        
        # Create a construction rule for the entity
        source_rule = Rule.construction(
            tool="load_csv",
            args={"source_file": "people.csv"}
        )
        
        person.add_rule(source_rule)
        
        assert len(person.rules) == 1
        assert person.rules[0] == source_rule
        assert person.rules[0].is_construction()
        
        # Create a retrieval rule for the graph plan
        metadata_rule = Rule.retrieval(
            tool="cypher_query",
            args={"query": "MATCH (n:GraphPlan) RETURN n"}
        )
        
        # Add the rule directly to the graph plan
        graph_plan.add_rule(metadata_rule)
        
        # Verify the rule was added
        assert len(graph_plan.rules) == 1
        assert graph_plan.rules[0] == metadata_rule
        assert graph_plan.rules[0].is_retrieval()

    def test_entity_properties(self):
        """Test adding properties to entities."""
        person = EntityPlan(
            name="Person",
            description="A person entity"
        )
        
        person.add_property("name")
        person.add_property("age")
        
        assert len(person.property_keys) == 2
        assert "name" in person.property_keys
        assert "age" in person.property_keys

    def test_relation_properties(self):
        """Test adding properties to relations."""
        person = EntityPlan(
            name="Person",
            description="A person entity"
        )
        
        organization = EntityPlan(
            name="Organization",
            description="An organization entity"
        )
        
        works_for = RelationPlan(
            name="WORKS_FOR",
            description="Person works for an organization",
            from_entity=person,
            to_entity=organization
        )
        
        works_for.add_property("since")
        works_for.add_property("role")
        
        assert len(works_for.property_keys) == 2
        assert "since" in works_for.property_keys
        assert "role" in works_for.property_keys

    def test_serialization(self):
        """Test serializing and deserializing a graph plan."""
        # Create a graph plan with entities and relations
        graph_plan = GraphPlan(
            name="Test Graph Plan",
            description="A test graph plan"
        )
        
        # Add a source
        source = FileSource(
            file_path="people.csv",
            mime_type="text/csv",
            header=["id", "name", "age"],
            sample=[["1", "John", "30"], ["2", "Jane", "25"]]
        )
        graph_plan.add_source(source)
        
        person = EntityPlan(
            name="Person",
            description="A person entity"
        )
        person.add_property("name")
        
        organization = EntityPlan(
            name="Organization",
            description="An organization entity"
        )
        organization.add_property("name")
        
        graph_plan.add_entity(person)
        graph_plan.add_entity(organization)
        
        works_for = RelationPlan(
            name="WORKS_FOR",
            description="Person works for an organization",
            from_entity=person,
            to_entity=organization
        )
        works_for.add_property("since")
        
        graph_plan.add_relation(works_for)
        
        # Serialize to dictionary
        data = graph_plan.to_dict()
        
        # Deserialize back to a graph plan
        new_graph_plan = GraphPlan.from_dict(data)
        
        # Verify the deserialized graph plan
        assert new_graph_plan.name == "Test Graph Plan"
        assert new_graph_plan.description == "A test graph plan"
        assert len(new_graph_plan.entities) == 2
        assert len(new_graph_plan.relations) == 1
        assert len(new_graph_plan.sources) == 1
        
        # Verify sources were preserved
        assert "people.csv" in new_graph_plan.sources
        assert new_graph_plan.sources["people.csv"].mime_type == "text/csv"
        assert len(new_graph_plan.sources["people.csv"].header) == 3
        
        # Verify entity properties were preserved
        person_entity = new_graph_plan.find_entity_by_name("Person")
        assert person_entity is not None
        assert "name" in person_entity.property_keys
        
        # Verify relation properties were preserved
        relations = new_graph_plan.get_relations_for_entity(person_entity)
        assert len(relations) == 1
        assert relations[0].name == "WORKS_FOR"
        assert "since" in relations[0].property_keys
