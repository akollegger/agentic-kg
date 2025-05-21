"""
Entity plan module for the graph plan system.

This module contains the EntityPlan class which represents a node type definition
in a knowledge graph.
"""

from typing import List
from pydantic import Field

from .base import BasePlan
from .rule import Rule


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
