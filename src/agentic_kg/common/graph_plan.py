"""
# Graph Plan

A module for defining and managing knowledge graph plans containing schema along with instructions for knowledge graph construction, import and retrieval.

## Overview

A "graph plan" is like a blueprint for a knowledge graph, describing 
what the graph should look like, how it should be built, and how
it should be accessed.

The graph plan is itself a graph, with primary elements that are lightweight.
Rules can be attached to elements to provide additional
information for particular tasks. For example, an `EntityPlan` indicates a node type
definition, which may have a `construction_rule` to indicate the file it can
be constructed from. 
"""

import uuid
from typing import Dict, List, Optional
from enum import Enum   
from pydantic import BaseModel, Field


class FileSource(BaseModel):
    """Represents a file source which has been prepared and analyzed for import.
    
    Attributes:
        file_path: The path to the file
        mime_type: The MIME type of the file
        header: The column names of the file, if it is a CSV file
        sample: A sample of the file, if it is a CSV file
    """
    file_path: str
    mime_type: str
    header: Optional[List[str]] = None
    sample: Optional[List[List[str]]] = None

    def __str__(self):
        return f"FileSource(file_path={self.file_path}, mime_type={self.mime_type}, header={self.header}, sample={self.sample})"

class BasePlan(BaseModel):
    """
    Base class for all plan elements in the graph plan.
    
    Attributes:
        id: Unique identifier for the plan element
        name: Name of the plan element
        description: Description of what this plan element represents
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str


class RuleKind(str, Enum):
    """Enum representing the different kinds of rules."""
    CONSTRUCTION = "construction"
    RETRIEVAL = "retrieval"


class Rule(BasePlan):
    """
    Rule that can be attached to a GraphPlan, EntityPlan, or RelationPlan.
    Rules define how to construct or retrieve elements of the knowledge graph.
    
    Attributes:
        id: Unique identifier for the rule
        name: Name of the rule
        description: Description of what this rule does
        kind: The kind of rule (construction or retrieval)
        tool: Name of the tool to call for executing the rule
        args: Arguments to pass to the tool
    """
    kind: RuleKind
    tool: str
    args: Dict[str, str] = Field(default_factory=dict)
    
    @classmethod
    def construction(cls, name: str, description: str, tool: str, args: Dict[str, str] = None) -> 'Rule':
        """Factory method to create a construction rule.
        
        For construction rules, it's common to include a source_file in the args dictionary.
        """
        args = args or {}
        return cls(
            name=name,
            description=description,
            kind=RuleKind.CONSTRUCTION,
            tool=tool,
            args=args
        )
    
    @classmethod
    def retrieval(cls, name: str, description: str, tool: str, args: Dict[str, str] = None) -> 'Rule':
        """Factory method to create a retrieval rule."""
        return cls(
            name=name,
            description=description,
            kind=RuleKind.RETRIEVAL,
            tool=tool,
            args=args or {}
        )
        
    def is_construction(self) -> bool:
        """Check if this is a construction rule."""
        return self.kind == RuleKind.CONSTRUCTION
        
    def is_retrieval(self) -> bool:
        """Check if this is a retrieval rule."""
        return self.kind == RuleKind.RETRIEVAL


class EntityPlan(BasePlan):
    """
    Represents a node type definition in a knowledge graph.
    
    Attributes:
        id: Unique identifier for the entity
        name: Name of the entity (used as label in the graph)
        description: Description of what this entity represents
        property_keys: List of property keys for this entity
        rules: List of rules attached to this entity
    """
    property_keys: List[str] = Field(default_factory=list)
    rules: List[Rule] = Field(default_factory=list)
    
    def add_property(self, name: str) -> None:
        """Add a property key to this entity definition."""
        if name not in self.property_keys:
            self.property_keys.append(name)
    
    def add_rule(self, rule: Rule) -> None:
        """Add a rule to this entity."""
        self.rules.append(rule)


class RelationPlan(BasePlan):
    """
    Represents a relationship type definition in a knowledge graph.
    
    Attributes:
        id: Unique identifier for the relation
        name: Name of the relation (used as relationship type in the graph)
        description: Description of what this relation represents
        property_keys: List of property keys for this relation
        from_entity: Source entity for this relation
        to_entity: Target entity for this relation
        rules: List of rules attached to this relation
    """
    property_keys: List[str] = Field(default_factory=list)
    from_entity: 'EntityPlan'
    to_entity: 'EntityPlan'
    rules: List[Rule] = Field(default_factory=list)
    
    def add_property(self, name: str) -> None:
        """Add a property key to this relation definition."""
        if name not in self.property_keys:
            self.property_keys.append(name)
    
    def add_rule(self, rule: Rule) -> None:
        """Add a rule to this relation."""
        self.rules.append(rule)


class GraphPlan(BasePlan):
    """
    A blueprint for a knowledge graph, describing what the graph should look like,
    how it should be built, and how it should be accessed.
    
    Attributes:
        id: Unique identifier for the graph plan
        name: Name of the graph plan
        description: Description of what this graph plan represents
        entities: Dictionary of entity id to EntityPlan objects
        relations: Dictionary of relation id to RelationPlan objects
    """
    entities: Dict[str, EntityPlan] = Field(default_factory=dict)
    relations: Dict[str, RelationPlan] = Field(default_factory=dict)
    
    def add_entity(self, entity: EntityPlan) -> None:
        """Add an entity to this graph plan."""
        self.entities[entity.id] = entity
    
    def add_relation(self, relation: RelationPlan) -> None:
        """Add a relation to this graph plan."""
        self.relations[relation.id] = relation
    
    def find_entity_by_name(self, name: str) -> Optional[EntityPlan]:
        """Find an entity by its name.
        
        Note: This returns the first entity with a matching name. Names are not guaranteed
        to be unique, so multiple entities could have the same name.
        """
        for entity in self.entities.values():
            if entity.name == name:
                return entity
        return None
        
    # Keep the old method name for backward compatibility
    def get_entity_by_name(self, name: str) -> Optional[EntityPlan]:
        """Get an entity by its name (deprecated, use find_entity_by_name instead)."""
        return self.find_entity_by_name(name)
    
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
        
    # Keep the old method name for backward compatibility
    def get_relation_by_name(self, name: str) -> Optional[RelationPlan]:
        """Get a relation by its name (deprecated, use find_relation_by_name instead)."""
        return self.find_relation_by_name(name)
        
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
        """Convert the graph plan to a dictionary representation."""
        # Create a copy of the data to avoid modifying the original
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'entities': [],
            'relations': []
        }
        
        # Add entities as a list
        for entity in self.entities.values():
            entity_dict = {
                'id': entity.id,
                'name': entity.name,
                'description': entity.description,
                'property_keys': entity.property_keys,
                'rules': [rule.model_dump() for rule in entity.rules]
            }
            data['entities'].append(entity_dict)
        
        # Add relations as a list with entity references as IDs
        for relation in self.relations.values():
            relation_dict = {
                'id': relation.id,
                'name': relation.name,
                'description': relation.description,
                'property_keys': relation.property_keys,
                'from_entity': relation.from_entity.id,  # Just store the ID
                'to_entity': relation.to_entity.id,      # Just store the ID
                'rules': [rule.model_dump() for rule in relation.rules]
            }
            data['relations'].append(relation_dict)
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'GraphPlan':
        """Create a graph plan from a dictionary representation."""
        # Create a new graph plan
        graph_plan = cls(
            id=data.get('id', data.get('graph_plan_id', str(uuid.uuid4()))),
            name=data.get('name', data.get('graph_plan_name', 'Unnamed Graph Plan')),
            description=data.get('description', data.get('graph_plan_description', ''))
        )
        
        # Create entities first
        entity_map = {}
        for entity_data in data.get('entities', []):
            entity = EntityPlan(
                id=entity_data.get('id', entity_data.get('entity_id')),
                name=entity_data.get('name', entity_data.get('entity_name')),
                description=entity_data.get('description', entity_data.get('entity_description')),
                property_type_map=entity_data.get('property_type_map', {})
            )
            graph_plan.add_entity(entity)
            entity_map[entity.id] = entity
        
        # Create relations
        for relation_data in data.get('relations', []):
            # Get the from and to entities by ID
            from_entity_id = relation_data.get('from_entity')
            to_entity_id = relation_data.get('to_entity')
            
            from_entity = entity_map.get(from_entity_id)
            to_entity = entity_map.get(to_entity_id)
            
            if from_entity and to_entity:
                relation = RelationPlan(
                    id=relation_data.get('id', relation_data.get('relation_id')),
                    name=relation_data.get('name', relation_data.get('relation_name')),
                    description=relation_data.get('description', relation_data.get('relation_description')),
                    from_entity=from_entity,
                    to_entity=to_entity,
                    property_type_map=relation_data.get('property_type_map', {})
                )
                graph_plan.add_relation(relation)
        
        # Add rules
        if 'rules' in data:
            for rule_data in data['rules']:
                # Create rule based on its kind
                if 'kind' in rule_data and rule_data['kind'] in [RuleKind.CONSTRUCTION, RuleKind.RETRIEVAL]:
                    # New format rule
                    args = rule_data.get('args', {})
                    # Handle legacy source_file field by moving it to args
                    if 'source_file' in rule_data and rule_data['kind'] == RuleKind.CONSTRUCTION:
                        args = args.copy()
                        args['source_file'] = rule_data['source_file']
                    
                    rule = Rule(
                        id=rule_data.get('id', rule_data.get('rule_id', str(uuid.uuid4()))),
                        name=rule_data.get('name', rule_data.get('rule_name')),
                        description=rule_data.get('description', rule_data.get('rule_description')),
                        kind=rule_data['kind'],
                        tool=rule_data['tool'],
                        args=args
                    )
                    graph_plan.add_rule(rule)
                # Legacy format rules
                elif 'source_file' in rule_data and 'tool' in rule_data:
                    # Construction rule
                    args = rule_data.get('args', {}).copy()
                    args['source_file'] = rule_data['source_file']
                    
                    rule = Rule.construction(
                        name=rule_data.get('name', rule_data.get('rule_name')),
                        description=rule_data.get('description', rule_data.get('rule_description')),
                        tool=rule_data['tool'],
                        args=args
                    )
                    if 'rule_id' in rule_data or 'id' in rule_data:
                        rule.id = rule_data.get('id', rule_data.get('rule_id'))
                    graph_plan.add_rule(rule)
                elif 'tool' in rule_data:
                    # Retrieval rule
                    rule = Rule.retrieval(
                        name=rule_data.get('name', rule_data.get('rule_name')),
                        description=rule_data.get('description', rule_data.get('rule_description')),
                        tool=rule_data['tool'],
                        args=rule_data.get('args', {})
                    )
                    if 'rule_id' in rule_data or 'id' in rule_data:
                        rule.id = rule_data.get('id', rule_data.get('rule_id'))
                    graph_plan.add_rule(rule)
        
        return graph_plan
