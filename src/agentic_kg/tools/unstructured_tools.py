from google.adk.tools import ToolContext
from typing import Dict, Any
from agentic_kg.common.util import tool_success, tool_error
from .file_tools import search_file

PROPOSED_SCHEMA_EXTENSION = "proposed_schema_extension"
APPROVED_SCHEMA_EXTENSION = "approved_schema_extension"

def set_proposed_schema_extension(graph_schema: str, tool_context: ToolContext) -> Dict[str, Any]:
    f"""Saves a proposed extension to an existing graph schema

    Args:
        graph_schema: a description of the proposed schema extension
    """
    tool_context.state[PROPOSED_SCHEMA_EXTENSION] = graph_schema
    return tool_success(PROPOSED_SCHEMA_EXTENSION, graph_schema)

def get_proposed_schema_extension(tool_context: ToolContext) -> Dict[str, Any]:
    """Returns the current graph schema extension proposal."""
    if PROPOSED_SCHEMA_EXTENSION not in tool_context.state:
        return tool_error(f"{PROPOSED_SCHEMA_EXTENSION} not set.")  

    return tool_success(PROPOSED_SCHEMA_EXTENSION, tool_context.state.get(PROPOSED_SCHEMA_EXTENSION, ""))


def approve_proposed_schema_extension(tool_context:ToolContext) -> Dict[str, Any]:
    f"""Approves the {PROPOSED_SCHEMA_EXTENSION} in state for further processing as {APPROVED_SCHEMA_EXTENSION}."""
    
    if PROPOSED_SCHEMA_EXTENSION not in tool_context.state:
        return tool_error(f"{PROPOSED_SCHEMA_EXTENSION} not set")

    tool_context.state[APPROVED_SCHEMA_EXTENSION] = tool_context.state[PROPOSED_SCHEMA_EXTENSION]


def get_approved_schema_extension(tool_context: ToolContext) -> Dict[str, Any]:
    """Returns the approved graph schema, if it there is one."""
    if APPROVED_SCHEMA_EXTENSION not in tool_context.state:
        return tool_error(f"{APPROVED_SCHEMA_EXTENSION} not set.")  

    return tool_success(APPROVED_SCHEMA_EXTENSION, tool_context.state[APPROVED_SCHEMA_EXTENSION])

#  Tool: Propose Node Extension

PROPOSED_EXTENSION_PLAN = "proposed_extension_plan"

NAMED_ENTITY_EXTRACTION_RULE = "named_entity_extraction"

def propose_entity_extraction(proposed_kind: str, tool_context:ToolContext) -> dict:
    f"""Propose a named entity extraction for a kind of entity found in unstructured text.

    The extraction will be added to the plan {PROPOSED_EXTENSION_PLAN} dictionary of extension rules.

    The extension rule entry will have the following keys:
    - extension_type: "{NAMED_ENTITY_EXTRACTION_RULE}"
    - kind: The kind of entity to extract

    Args:
        proposed_kind: The kind of entity to extract
        
    Returns:
        dict: A dictionary containing metadata about the content.
                Includes a 'status' key ('success' or 'error').
                If 'success', includes a {NAMED_ENTITY_EXTRACTION_RULE} key with the construction plan for the node
                If 'error', includes an 'error_message' key.
                The 'error_message' may have instructions about how to handle the error.
    """
    extension_plan = tool_context.state.get(PROPOSED_EXTENSION_PLAN, {})
    ner_rule = {
        "construction_type": NAMED_ENTITY_EXTRACTION_RULE,
        "kind": proposed_kind
    }   
    extension_plan[proposed_kind] = ner_rule
    tool_context.state[PROPOSED_EXTENSION_PLAN] = extension_plan
    return tool_success(NAMED_ENTITY_EXTRACTION_RULE, ner_rule)


def remove_entity_extraction(kind_of_entity: str, tool_context:ToolContext) -> dict:
    """Remove a named entity extraction rule from the proposed extension plan based on kind.

    Args:
        kind_of_entity: The kind of entity which should be removed from the extension plan

    Returns:
        dict: A dictionary containing metadata about the content.
                Includes a 'status' key ('success' or 'error').
                If 'success', includes a 'ner_rule_removed' key with the label of the removed node construction
                If 'error', includes an 'error_message' key.
                The 'error_message' may have instructions about how to handle the error.
    """
    extension_plan = tool_context.state.get(PROPOSED_EXTENSION_PLAN, {})
    if node_label not in extension_plan:
       return tool_success("ner_rule_removed", "node construction rule not found. removal not needed.")

    extension_plan.pop(node_label)

    tool_context.state[PROPOSED_EXTENSION_PLAN] = extension_plan
    return tool_success("ner_rule_removed", node_label)


APPROVED_EXTENSION_PLAN = "approved_extension_plan"

# Tool: Approve the proposed extension plan
def approve_proposed_extension_plan(tool_context:ToolContext) -> dict:
    """Approve the proposed extension plan."""
    tool_context.state[APPROVED_EXTENSION_PLAN] = tool_context.state.get(PROPOSED_EXTENSION_PLAN)
    return tool_success(APPROVED_EXTENSION_PLAN, tool_context.state[APPROVED_EXTENSION_PLAN])

# Tool: Get Proposed extension Plan

def get_proposed_extension_plan(tool_context:ToolContext) -> dict:
    """Get the proposed construction plan."""
    return tool_context.state.get(PROPOSED_EXTENSION_PLAN, [])


def get_approved_extension_plan(tool_context:ToolContext) -> dict:
    """Get the approved construction plan."""
    return tool_context.state.get(APPROVED_EXTENSION_PLAN, [])


PROPOSED_ENTITIES = "proposed_entities"
APPROVED_ENTITIES = "approved_entities"

def set_proposed_entities(proposed_entities: list[str], tool_context:ToolContext) -> dict:
    """Sets the list proposed entities to extract from unstructured text."""
    tool_context.state[PROPOSED_ENTITIES] = proposed_entities
    return tool_success(PROPOSED_ENTITIES, proposed_entities)

def get_proposed_entities(tool_context:ToolContext) -> dict:
    """Gets the list proposed entities to extract from unstructured text."""
    return tool_context.state.get(PROPOSED_ENTITIES, [])

def approved_proposed_entities(tool_context:ToolContext) -> dict:
    """Approves the proposed entities to extract from unstructured text."""
    tool_context.state[APPROVED_ENTITIES] = tool_context.state.get(PROPOSED_ENTITIES)
    return tool_success(APPROVED_ENTITIES, tool_context.state[APPROVED_ENTITIES])

def get_approved_entities(tool_context:ToolContext) -> dict:
    """Get the approved list of kinds of entities."""
    return tool_context.state.get(APPROVED_ENTITIES, [])

PROPOSED_PREDICATES = "proposed_predicates"
APPROVED_PREDICATES = "approved_predicates"

def add_proposed_predicate(label: str, from_label:str, to_label:str, properties: list[str], tool_context:ToolContext) -> dict:
    """Add a proposed predicate to the proposed extension plan.

    Args:
        label: The label of the predicate. This is the kind of relationahip between two entities. For example, "LIKES"
        from_label: The label of the entity that the predicate is from. For example, "Person"
        to_label: The label of the entity that the predicate is to. For example, "Beverage"
        properties: The properties of the predicate. For example, ["intensity"]
    """
    current_predicates = tool_context.state.get(PROPOSED_PREDICATES, {})
    current_predicates[label] = {"label": label, "from_label": from_label, "to_label": to_label, "properties": properties}
    tool_context.state[PROPOSED_PREDICATES] = current_predicates
    return tool_success(PROPOSED_PREDICATES, current_predicates)


def remove_proposed_predicate(label: str, tool_context:ToolContext) -> dict:
    """Remove a proposed predicate from the proposed extension plan."""
    current_predicates = tool_context.state.get(PROPOSED_PREDICATES, {})
    if label not in current_predicates:
        return tool_success("predicate_removed", f"Predicate {label} not found in proposed predicates. Removal not needed.")
    current_predicates.pop(label)
    tool_context.state[PROPOSED_PREDICATES] = current_predicates
    return tool_success("predicate_removed", current_predicates)
    
def get_proposed_predicates(tool_context:ToolContext) -> dict:
    """Get the proposed predicates."""
    return tool_context.state.get(PROPOSED_PREDICATES, {})


def approve_proposed_predicates(tool_context:ToolContext) -> dict:
    """Approve the proposed predicates."""
    tool_context.state[APPROVED_PREDICATES] = tool_context.state.get(PROPOSED_PREDICATES)
    return tool_success(APPROVED_PREDICATES, tool_context.state[APPROVED_PREDICATES])
    
def get_approved_predicates(tool_context:ToolContext) -> dict:
    """Get the approved predicates."""
    return tool_context.state.get(APPROVED_PREDICATES, {})
