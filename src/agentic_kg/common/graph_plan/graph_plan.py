"""
Graph plan module for the graph plan system.

This module contains the GraphPlan class which serves as a blueprint for a knowledge graph,
describing what the graph should look like, how it should be built, and how it should be accessed.
"""

import uuid
from typing import Dict, List, Optional
from pydantic import Field

from .base import BasePlan
from .file_source import FileSource
from .entity_plan import EntityPlan
from .relation_plan import RelationPlan
from .rule import Rule, RuleKind


class GraphPlan(BasePlan):
    """
    A blueprint for a knowledge graph, describing what the graph should look like,
    how it should be built, and how it should be accessed.
    
    Attributes:
        id: Unique identifier for the graph plan
        name: Name of the graph plan
        description: Description of what this graph plan represents
        sources: Dictionary of filename to FileSource objects
        entities: Dictionary of entity id to EntityPlan objects
        relations: Dictionary of relation id to RelationPlan objects
        rules: List of rules attached to this graph plan
    """
    sources: Dict[str, FileSource] = Field(default_factory=dict, description="Map from filename to FileSource")
    entities: Dict[str, EntityPlan] = Field(default_factory=dict, description="Map from entity id to EntityPlan")
    relations: Dict[str, RelationPlan] = Field(default_factory=dict, description="Map from relation id to RelationPlan")
    rules: List[Rule] = Field(default_factory=list, description="Rules attached to this graph plan")
    
    def add_source(self, source: FileSource) -> None:
        """Add a file source to this graph plan."""
        self.sources[source.file_path] = source
    
    def add_entity(self, entity: EntityPlan) -> None:
        """Add an entity to this graph plan."""
        self.entities[entity.id] = entity
    
    def add_relation(self, relation: RelationPlan) -> None:
        """Add a relation to this graph plan."""
        self.relations[relation.id] = relation
        
    def add_rule(self, rule: Rule) -> None:
        """Add a rule to this graph plan."""
        self.rules.append(rule)
    
    def find_entity_by_name(self, name: str) -> Optional[EntityPlan]:
        """Find an entity by its name.
        
        Note: This returns the first entity with a matching name. Names are not guaranteed
        to be unique, so multiple entities could have the same name.
        """
        for entity in self.entities.values():
            if entity.name == name:
                return entity
        return None
    
    def get_entity_by_id(self, id: str) -> Optional[EntityPlan]:
        """Get an entity by its ID."""
        return self.entities.get(id)
        
    def find_relation_by_name(self, name: str) -> Optional[RelationPlan]:
        """Find a relation by its name.
        
        Note: This returns the first relation with a matching name. Names are not guaranteed
        to be unique, so multiple relations could have the same name.
        
        Args:
            name: Name of the relation to find
            
        Returns:
            The relation if found, None otherwise
        """
        for relation in self.relations.values():
            if relation.name == name:
                return relation
        return None
        
    def create_relation(self, name: str, description: str, 
                       from_name: str, to_name: str) -> RelationPlan:
        """Create a relation between two entities by their names.
        
        Args:
            name: Name of the relation
            description: Description of the relation
            from_name: Name of the source entity
            to_name: Name of the target entity
            
        Returns:
            The created relation
            
        Raises:
            ValueError: If either the from_name or to_name cannot be found by name
        """
        from_entity = self.find_entity_by_name(from_name)
        to_entity = self.find_entity_by_name(to_name)
        
        if from_entity is None:
            raise ValueError(f"Source entity with name '{from_name}' not found")
        if to_entity is None:
            raise ValueError(f"Target entity with name '{to_name}' not found")
            
        relation = RelationPlan(
            name=name,
            description=description,
            from_entity=from_entity,
            to_entity=to_entity
        )
        
        self.add_relation(relation)
        return relation
    
    def get_relations_for_entity(self, entity: EntityPlan) -> List[RelationPlan]:
        """Get all relations where the given entity is either the source or target."""
        return [r for r in self.relations.values() if r.from_entity == entity or r.to_entity == entity]
    
    def to_dict(self) -> Dict:
        """Convert the graph plan to a dictionary representation.
        
        This method delegates to the serialization module to avoid cluttering
        the GraphPlan class with serialization logic.
        
        Returns:
            A dictionary representation of the graph plan
        """
        from .serialization import graph_plan_to_dict
        return graph_plan_to_dict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'GraphPlan':
        """Create a graph plan from a dictionary representation.
        
        This method delegates to the serialization module to avoid cluttering
        the GraphPlan class with deserialization logic.
        
        Args:
            data: The dictionary representation of the graph plan
            
        Returns:
            A new GraphPlan instance
        """
        from .serialization import graph_plan_from_dict
        return graph_plan_from_dict(data)
