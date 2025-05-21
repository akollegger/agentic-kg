"""
Rule module for the graph plan system.

This module contains the Rule class and related components that define
how to construct or retrieve elements of a knowledge graph.
"""

from enum import Enum
from typing import Dict, Optional
from pydantic import Field

from .base import BasePlan


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
