"""
Serialization module for the graph plan system.

This module contains functions for serializing and deserializing graph plans to and from
dictionary representations, which can then be easily converted to JSON or other formats.
"""

import uuid
from typing import Dict, Any, TYPE_CHECKING, Type

from .file_source import FileSource
from .entity_plan import EntityPlan
from .relation_plan import RelationPlan
from .rule import Rule, RuleKind

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from .graph_plan import GraphPlan


def graph_plan_to_dict(graph_plan: 'GraphPlan') -> Dict[str, Any]:
    """Convert a graph plan to a dictionary representation.
    
    Args:
        graph_plan: The graph plan to convert
        
    Returns:
        A dictionary representation of the graph plan
    """
    # Create a copy of the data to avoid modifying the original
    data = {
        'id': graph_plan.id,
        'name': graph_plan.name,
        'description': graph_plan.description,
        'entities': [],
        'relations': [],
        'sources': {},
        'rules': []
    }
    
    # Add entities as a list
    for entity in graph_plan.entities.values():
        entity_dict = {
            'id': entity.id,
            'name': entity.name,
            'description': entity.description,
            'property_keys': entity.property_keys,
            'rules': [rule.model_dump() for rule in entity.rules]
        }
        data['entities'].append(entity_dict)
    
    # Add relations as a list with entity references as IDs
    for relation in graph_plan.relations.values():
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
    for file_path, source in graph_plan.sources.items():
        data['sources'][file_path] = source.model_dump()
        
    # Add rules attached to the graph plan
    for rule in graph_plan.rules:
        data['rules'].append(rule.model_dump())
    
    return data


def graph_plan_from_dict(data: Dict[str, Any]) -> 'GraphPlan':
    """Create a graph plan from a dictionary representation.
    
    Args:
        data: The dictionary representation of the graph plan
        
    Returns:
        A new GraphPlan instance
    """
    # Import here to avoid circular imports
    from .graph_plan import GraphPlan
    
    # Create a new graph plan
    graph_plan = GraphPlan(
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
