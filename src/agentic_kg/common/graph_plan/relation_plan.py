"""
Relation plan module for the graph plan system.

This module contains the RelationPlan class which represents a relationship type
definition in a knowledge graph.
"""

from typing import List
from pydantic import Field

from .base import BasePlan
from .rule import Rule
from .entity_plan import EntityPlan


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
    from_entity: EntityPlan
    to_entity: EntityPlan
    rules: List[Rule] = Field(default_factory=list)
    
    def add_property(self, name: str) -> None:
        """Add a property key to this relation definition."""
        if name not in self.property_keys:
            self.property_keys.append(name)
    
    def add_rule(self, rule: Rule) -> None:
        """Add a rule to this relation."""
        self.rules.append(rule)
