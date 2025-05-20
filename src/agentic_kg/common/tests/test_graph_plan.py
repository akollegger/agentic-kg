"""
Unit tests for the graph_plan module.
"""

import pytest
from pydantic import ValidationError

from ..graph_plan import GraphPlan, Entity, Relation, ConstructionAnnotation, RetrievalAnnotation


class TestGraphPlan:
    """Tests for the GraphPlan class and related components."""

    def test_create_graph_plan(self):
        """Test creating a basic graph plan."""
        graph_plan = GraphPlan(
            graph_plan_name="Test Graph Plan",
            graph_plan_description="A test graph plan"
        )
        
        assert graph_plan.graph_plan_id is not None
        assert graph_plan.graph_plan_name == "Test Graph Plan"
        assert graph_plan.graph_plan_description == "A test graph plan"
        assert len(graph_plan.entities) == 0
        assert len(graph_plan.relations) == 0
        assert len(graph_plan.annotations) == 0

    def test_add_entity(self):
        """Test adding an entity to a graph plan."""
        graph_plan = GraphPlan(
            graph_plan_name="Test Graph Plan",
            graph_plan_description="A test graph plan"
        )
        
        entity = Entity(
            entity_name="Person",
            entity_description="A person entity"
        )
        
        graph_plan.add_entity(entity)
        
        assert len(graph_plan.entities) == 1
        assert entity.entity_id in graph_plan.entities
        assert graph_plan.entities[entity.entity_id] == entity
        
        # Test retrieving by name
        retrieved_entity = graph_plan.get_entity_by_name("Person")
        assert retrieved_entity == entity
        
        # Test retrieving by ID
        retrieved_entity = graph_plan.get_entity_by_id(entity.entity_id)
        assert retrieved_entity == entity

    def test_add_relation(self):
        """Test adding a relation between entities."""
        graph_plan = GraphPlan(
            graph_plan_name="Test Graph Plan",
            graph_plan_description="A test graph plan"
        )
        
        person = Entity(
            entity_name="Person",
            entity_description="A person entity"
        )
        
        organization = Entity(
            entity_name="Organization",
            entity_description="An organization entity"
        )
        
        graph_plan.add_entity(person)
        graph_plan.add_entity(organization)
        
        works_for = Relation(
            relation_name="WORKS_FOR",
            relation_description="Person works for an organization",
            from_entity=person,
            to_entity=organization
        )
        
        graph_plan.add_relation(works_for)
        
        assert len(graph_plan.relations) == 1
        assert works_for.relation_id in graph_plan.relations
        assert graph_plan.relations[works_for.relation_id] == works_for
        
        # Test retrieving relations for an entity
        person_relations = graph_plan.get_relations_for_entity(person)
        assert len(person_relations) == 1
        assert person_relations[0] == works_for
        
        org_relations = graph_plan.get_relations_for_entity(organization)
        assert len(org_relations) == 1
        assert org_relations[0] == works_for

    def test_add_annotation(self):
        """Test adding annotations to graph plan elements."""
        graph_plan = GraphPlan(
            graph_plan_name="Test Graph Plan",
            graph_plan_description="A test graph plan"
        )
        
        person = Entity(
            entity_name="Person",
            entity_description="A person entity"
        )
        
        graph_plan.add_entity(person)
        
        # Create an annotation for the entity
        source_annotation = ConstructionAnnotation(
            annotation_name="Source",
            annotation_description="Data source for this entity",
            annotates=person,
            source_file="people.csv",
            transformation="direct_import"
        )
        
        person.add_annotation(source_annotation)
        
        assert len(person.annotations) == 1
        assert person.annotations[0] == source_annotation
        # Annotation no longer has property_type_map
        
        # Create an annotation for the graph plan
        metadata_annotation = RetrievalAnnotation(
            annotation_name="Metadata",
            annotation_description="Retrieval pattern for the graph plan",
            annotates=graph_plan,
            query_pattern="MATCH (n:GraphPlan) RETURN n",
            access_method="cypher"
        )
        
        graph_plan.add_annotation(metadata_annotation)
        
        assert len(graph_plan.annotations) == 1
        assert graph_plan.annotations[0] == metadata_annotation
        # Annotation no longer has property_type_map

    def test_entity_properties(self):
        """Test adding properties to entities."""
        person = Entity(
            entity_name="Person",
            entity_description="A person entity"
        )
        
        person.add_property("name", "String")
        person.add_property("age", "Integer")
        
        assert len(person.property_type_map) == 2
        assert person.property_type_map["name"] == "String"
        assert person.property_type_map["age"] == "Integer"

    def test_relation_properties(self):
        """Test adding properties to relations."""
        person = Entity(
            entity_name="Person",
            entity_description="A person entity"
        )
        
        organization = Entity(
            entity_name="Organization",
            entity_description="An organization entity"
        )
        
        works_for = Relation(
            relation_name="WORKS_FOR",
            relation_description="Person works for an organization",
            from_entity=person,
            to_entity=organization
        )
        
        works_for.add_property("since", "Date")
        works_for.add_property("role", "String")
        
        assert len(works_for.property_type_map) == 2
        assert works_for.property_type_map["since"] == "Date"
        assert works_for.property_type_map["role"] == "String"

    def test_serialization(self):
        """Test serializing and deserializing a graph plan."""
        # Create a graph plan with entities and relations
        graph_plan = GraphPlan(
            graph_plan_name="Test Graph Plan",
            graph_plan_description="A test graph plan"
        )
        
        person = Entity(
            entity_name="Person",
            entity_description="A person entity"
        )
        person.add_property("name", "String")
        
        organization = Entity(
            entity_name="Organization",
            entity_description="An organization entity"
        )
        organization.add_property("name", "String")
        
        graph_plan.add_entity(person)
        graph_plan.add_entity(organization)
        
        works_for = Relation(
            relation_name="WORKS_FOR",
            relation_description="Person works for an organization",
            from_entity=person,
            to_entity=organization
        )
        works_for.add_property("since", "Date")
        
        graph_plan.add_relation(works_for)
        
        # Serialize to dictionary
        data = graph_plan.to_dict()
        
        # Deserialize back to a graph plan
        new_graph_plan = GraphPlan.from_dict(data)
        
        # Verify the deserialized graph plan
        assert new_graph_plan.graph_plan_name == "Test Graph Plan"
        assert new_graph_plan.graph_plan_description == "A test graph plan"
        assert len(new_graph_plan.entities) == 2
        assert len(new_graph_plan.relations) == 1
        
        # Verify entity properties were preserved
        person_entity = new_graph_plan.get_entity_by_name("Person")
        assert person_entity is not None
        assert person_entity.property_type_map["name"] == "String"
        
        # Verify relation properties were preserved
        relations = new_graph_plan.get_relations_for_entity(person_entity)
        assert len(relations) == 1
        assert relations[0].relation_name == "WORKS_FOR"
        assert relations[0].property_type_map["since"] == "Date"
