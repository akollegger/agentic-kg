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
        """Convert the graph plan to a dictionary representation."""
        # Create a copy of the data to avoid modifying the original
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'entities': [],
            'relations': [],
            'sources': {},
            'rules': []
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
            
        # Add sources as a dictionary with file_path as key
        for file_path, source in self.sources.items():
            data['sources'][file_path] = source.model_dump()
            
        # Add rules attached to the graph plan
        for rule in self.rules:
            data['rules'].append(rule.model_dump())
        
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
        
        # Add sources if present
        if 'sources' in data:
            for file_path, source_data in data['sources'].items():
                source = FileSource(**source_data)
                graph_plan.add_source(source)
        
        # Create entities first
        entity_map = {}
        for entity_data in data.get('entities', []):
            entity = EntityPlan(
                id=entity_data.get('id', entity_data.get('entity_id')),
                name=entity_data.get('name', entity_data.get('entity_name')),
                description=entity_data.get('description', entity_data.get('entity_description')),
                property_keys=entity_data.get('property_keys', [])
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
                    property_keys=relation_data.get('property_keys', [])
                )
                graph_plan.add_relation(relation)
                
                # Add rules to the relation
                for rule_data in relation_data.get('rules', []):
                    rule = Rule(
                        id=rule_data.get('id', rule_data.get('rule_id', str(uuid.uuid4()))),
                        name=rule_data.get('name', rule_data.get('rule_name')),
                        description=rule_data.get('description', rule_data.get('rule_description')),
                        kind=rule_data.get('kind', RuleKind.CONSTRUCTION),
                        tool=rule_data.get('tool', ''),
                        args=rule_data.get('args', {})
                    )
                    relation.add_rule(rule)
        
        # Add rules to entities
        for entity_data in data.get('entities', []):
            entity_id = entity_data.get('id', entity_data.get('entity_id'))
            entity = graph_plan.entities.get(entity_id)
            
            if entity:
                for rule_data in entity_data.get('rules', []):
                    rule = Rule(
                        id=rule_data.get('id', rule_data.get('rule_id', str(uuid.uuid4()))),
                        name=rule_data.get('name', rule_data.get('rule_name')),
                        description=rule_data.get('description', rule_data.get('rule_description')),
                        kind=rule_data.get('kind', RuleKind.CONSTRUCTION),
                        tool=rule_data.get('tool', ''),
                        args=rule_data.get('args', {})
                    )
                    entity.add_rule(rule)
        
        # Add rules to the graph plan
        for rule_data in data.get('rules', []):
            rule = Rule(
                id=rule_data.get('id', rule_data.get('rule_id', str(uuid.uuid4()))),
                name=rule_data.get('name', rule_data.get('rule_name')),
                description=rule_data.get('description', rule_data.get('rule_description')),
                kind=rule_data.get('kind', RuleKind.CONSTRUCTION),
                tool=rule_data.get('tool', ''),
                args=rule_data.get('args', {})
            )
            graph_plan.add_rule(rule)
        
        return graph_plan
