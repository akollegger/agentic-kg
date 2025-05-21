"""
Graph Plan

A module for defining and managing knowledge graph plans containing schema along with 
instructions for knowledge graph construction, import and retrieval.

## Overview

A "graph plan" is like a blueprint for a knowledge graph, describing 
what the graph should look like, how it should be built, and how
it should be accessed.

The graph plan is itself a graph, with primary elements representing the schema of the graph.
Rules can be attached to elements to provide additional
information for particular tasks. For example, an `EntityPlan` indicates a node type
definition, which may have a `construction_rule` to indicate the file it can
be constructed from. 
"""

from .base import BasePlan
from .file_source import FileSource
from .rule import Rule, RuleKind
from .entity_plan import EntityPlan
from .relation_plan import RelationPlan
from .graph_plan import GraphPlan
from .serialization import graph_plan_to_dict, graph_plan_from_dict

__all__ = [
    'BasePlan',
    'FileSource',
    'Rule',
    'RuleKind',
    'EntityPlan',
    'RelationPlan',
    'GraphPlan',
    'graph_plan_to_dict',
    'graph_plan_from_dict',
]
