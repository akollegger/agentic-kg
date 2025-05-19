"""
# Graph Plan

A module for defining and managing knowledge graph plans containing schema along with instructions for knowledge graph construction, import and retrieval.

## Overview

A "graph plan" is like a blueprint for a knowledge graph, describing 
what the graph should look like, how it should be built, and how
it should be accessed.

The graph plan is itself a graph, with primary elements that are lightweight.
Annotation elements can be attached to primary elements to provide additional
information for particular tasks. For example, an `Entity` indicates a node type
definition, which may have a `Source` annotation to indicate the file it can
be constructed from. 

## Design

The graph plan has the following primary elements (using Pydantic type specifications):

```python
class GraphPlan(BaseModel):
    graph_plan_id: str
    graph_plan_name: str
    graph_plan_description: str
    entities: Dict[str, Entity] = {}
    relations: Dict[str, Relation] = {}
    annotations: List[Annotation] = []

class Entity(BaseModel):
    entity_id: str
    entity_name: str
    entity_description: str
    properties: Dict[str, str] = {}
    annotations: List[Annotation] = []

class Relation(BaseModel):
    relation_id: str
    relation_name: str
    relation_description: str
    properties: Dict[str, str] = {}
    from_entity: Entity
    to_entity: Entity
    annotations: List[Annotation] = []

class Annotation(BaseModel):
    annotation_id: str
    annotation_name: str
    annotation_description: str
    properties: Dict[str, str] = {}
    annotates: Union[GraphPlan, Entity, Relation]
```
"""

import uuid
from typing import Dict, List, Optional, Set, Union, ForwardRef
from pydantic import BaseModel, Field

# Forward references for type hints
GraphPlanRef = ForwardRef('GraphPlan')
EntityRef = ForwardRef('Entity')
RelationRef = ForwardRef('Relation')


class Annotation(BaseModel):
    """
    Represents an annotation that can be attached to a GraphPlan, Entity, or Relation.
    
    Attributes:
        annotation_id: Unique identifier for the annotation
        annotation_name: Name of the annotation
        annotation_description: Description of what this annotation represents
        properties: Dictionary of property names to their values
        annotates: The element this annotation is attached to
    """
    annotation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    annotation_name: str
    annotation_description: str
    properties: Dict[str, str] = Field(default_factory=dict)
    annotates: Union[GraphPlanRef, EntityRef, RelationRef]


class Entity(BaseModel):
    """
    Represents a node type definition in a knowledge graph.
    
    Attributes:
        entity_id: Unique identifier for the entity
        entity_name: Name of the entity (used as label in the graph)
        entity_description: Description of what this entity represents
        properties: Dictionary of property names to their types
        annotations: List of annotations attached to this entity
    """
    entity_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    entity_name: str
    entity_description: str
    properties: Dict[str, str] = Field(default_factory=dict)
    annotations: List[Annotation] = Field(default_factory=list)
    
    def add_property(self, name: str, property_type: str) -> None:
        """Add a property to this entity definition."""
        self.properties[name] = property_type
    
    def add_annotation(self, annotation: Annotation) -> None:
        """Add an annotation to this entity."""
        annotation.annotates = self
        self.annotations.append(annotation)


class Relation(BaseModel):
    """
    Represents a relationship type definition in a knowledge graph.
    
    Attributes:
        relation_id: Unique identifier for the relation
        relation_name: Name of the relation (used as relationship type in the graph)
        relation_description: Description of what this relation represents
        from_entity: The source entity for this relation
        to_entity: The target entity for this relation
        properties: Dictionary of property names to their types
        annotations: List of annotations attached to this relation
    """
    relation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    relation_name: str
    relation_description: str
    properties: Dict[str, str] = Field(default_factory=dict)
    from_entity: Entity
    to_entity: Entity
    annotations: List[Annotation] = Field(default_factory=list)
    
    def add_property(self, name: str, property_type: str) -> None:
        """Add a property to this relation definition."""
        self.properties[name] = property_type
    
    def add_annotation(self, annotation: Annotation) -> None:
        """Add an annotation to this relation."""
        annotation.annotates = self
        self.annotations.append(annotation)


class GraphPlan(BaseModel):
    """
    A blueprint for a knowledge graph, describing what the graph should look like,
    how it should be built, and how it should be accessed.
    
    Attributes:
        graph_plan_id: Unique identifier for the graph plan
        graph_plan_name: Name of the graph plan
        graph_plan_description: Description of what this graph plan represents
        entities: Dictionary of entity_id to Entity objects
        relations: Dictionary of relation_id to Relation objects
        annotations: List of annotations attached to this graph plan
    """
    graph_plan_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    graph_plan_name: str
    graph_plan_description: str
    entities: Dict[str, Entity] = Field(default_factory=dict)
    relations: Dict[str, Relation] = Field(default_factory=dict)
    annotations: List[Annotation] = Field(default_factory=list)
    
    def add_entity(self, entity: Entity) -> None:
        """Add an entity to this graph plan."""
        self.entities[entity.entity_id] = entity
    
    def add_relation(self, relation: Relation) -> None:
        """Add a relation to this graph plan."""
        self.relations[relation.relation_id] = relation
    
    def add_annotation(self, annotation: Annotation) -> None:
        """Add an annotation to this graph plan."""
        annotation.annotates = self
        self.annotations.append(annotation)
    
    def get_entity_by_name(self, name: str) -> Optional[Entity]:
        """Get an entity by its name."""
        for entity in self.entities.values():
            if entity.entity_name == name:
                return entity
        return None
    
    def get_entity_by_id(self, entity_id: str) -> Optional[Entity]:
        """Get an entity by its ID."""
        return self.entities.get(entity_id)
    
    def get_relations_for_entity(self, entity: Entity) -> List[Relation]:
        """Get all relations where the given entity is either the source or target."""
        return [r for r in self.relations.values() if r.from_entity == entity or r.to_entity == entity]
    
    def to_dict(self) -> Dict:
        """Convert the graph plan to a dictionary representation."""
        # Use Pydantic's model_dump method but exclude circular references
        data = self.model_dump(exclude={'annotations': {'__all__': {'annotates'}}})
        
        # Convert entities and relations from dict to list for serialization
        if 'entities' in data:
            data['entities'] = list(data['entities'].values())
        if 'relations' in data:
            data['relations'] = list(data['relations'].values())
            
            # Replace entity references with entity IDs
            for relation in data['relations']:
                if 'from_entity' in relation:
                    relation['from_entity'] = relation['from_entity']['entity_id']
                if 'to_entity' in relation:
                    relation['to_entity'] = relation['to_entity']['entity_id']
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'GraphPlan':
        """Create a graph plan from a dictionary representation."""
        # Create a new graph plan
        graph_plan = cls(
            graph_plan_id=data['graph_plan_id'],
            graph_plan_name=data['graph_plan_name'],
            graph_plan_description=data['graph_plan_description']
        )
        
        # Create entities first
        entity_map = {}
        for entity_data in data.get('entities', []):
            entity = Entity(
                entity_id=entity_data['entity_id'],
                entity_name=entity_data['entity_name'],
                entity_description=entity_data['entity_description'],
                properties=entity_data.get('properties', {})
            )
            graph_plan.add_entity(entity)
            entity_map[entity.entity_id] = entity
        
        # Create relations
        for relation_data in data.get('relations', []):
            # Get the from and to entities by ID
            from_entity_id = relation_data.get('from_entity')
            to_entity_id = relation_data.get('to_entity')
            
            from_entity = entity_map.get(from_entity_id)
            to_entity = entity_map.get(to_entity_id)
            
            if from_entity and to_entity:
                relation = Relation(
                    relation_id=relation_data['relation_id'],
                    relation_name=relation_data['relation_name'],
                    relation_description=relation_data['relation_description'],
                    from_entity=from_entity,
                    to_entity=to_entity,
                    properties=relation_data.get('properties', {})
                )
                graph_plan.add_relation(relation)
        
        # Add annotations
        if 'annotations' in data:
            for annotation_data in data['annotations']:
                annotation = Annotation(
                    annotation_id=annotation_data['annotation_id'],
                    annotation_name=annotation_data['annotation_name'],
                    annotation_description=annotation_data['annotation_description'],
                    properties=annotation_data.get('properties', {})
                )
                graph_plan.add_annotation(annotation)
        
        return graph_plan


# Resolve forward references
Annotation.model_rebuild()
