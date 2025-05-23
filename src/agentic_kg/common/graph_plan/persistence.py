"""

This module provides persistence for the graph plans, using Neo4j for storage and retrieval.

## Property Graph Node Types

As a property graph, a graph plan is composed of the following node types (in pseudo-Cypher):

```
(plan:GraphPlan {id: <id>, name: <name>, description: <description>})
(source:FileSource {file_path: <file_path>, mime_type: <mime_type>, header: <header>, sample: <sample>})
(entity:EntityPlan {id: <entity_id>, name: <entity_name>, description: <entity_description>})
(relation:RelationPlan {id: <relation_id>, name: <relation_name>, description: <relation_description>})
```

Rules come in two kinds: construction and retrieval. These are indicated by extra labels. For example:

```
(rule:Rule:Construction {id: <rule_id>, tool: <rule_tool>, arg_*: <rule_args>})
(rule:Rule:Retrieval {id: <rule_id>, tool: <rule_tool>, arg_*: <rule_args>})
```

Rules have additional properties, prefixed with `arg_`, which map to/from the RulePlan `args` dictionary.
For example, a construction rule that uses a tool called `analyze_file` might take a file name as an argument:

```
(rule:Rule:Construction {
    id: "01234",
    tool: "analyze_file",
    arg_file_name: "some_file_name"
})
```

## Property Graph Relationship Types

The following relationship types connected the elements of the graph plan into a mini-graph:

```
(:GraphPlan)-[:HAS_SOURCE]->(:FileSource)
(:GraphPlan)-[:HAS_ENTITY]->(:EntityPlan)
(:GraphPlan)-[:HAS_RELATION]->(:RelationPlan)

(:EntityPlan)-[:HAS_RULE]->(:Rule)
(:RelationPlan)-[:HAS_RULE]->(:Rule)

(:Rule)-[:USES_FILE]->(:FileSource)
```

"""

from typing import Dict, Optional
from pydantic import Field

from .graph_plan import GraphPlan
from .file_source import FileSource
from .entity_plan import EntityPlan
from .relation_plan import RelationPlan
from .rule import Rule, RuleKind

from ..neo4j_for_adk import graphdb

def store_graph_plan(graph_plan: GraphPlan) -> None:
    """Store a graph plan in the property graph.
      This entirely replaces an existing sub-graph holding the graph plan.
    """
    def store_graph_plan_tx(tx, graph_plan: GraphPlan):
        # Remove the entire graph_plan sub-graph (these are isolated parts of the graph, so nothing else should be affected)
        tx.run("""
            MATCH p=(graph_plan:GraphPlan {id: $id})-[*1..3]-()
            DETACH DELETE p
            """,
            {"id": graph_plan.id}
        )
        # re-create the root GraphPlan node (this uses CREATE since we should've just removed any previous graph plan)
        tx.run("""
            CREATE (graph_plan:GraphPlan {id: $id})
            SET graph_plan.name = $name,
                graph_plan.description = $description
            """,
            {"id": graph_plan.id, "name": graph_plan.name, "description": graph_plan.description}
        )
        # Add sources
        for source in graph_plan.sources.values():
            tx.run("""
                MERGE (source:FileSource {file_path: $file_path})
                SET source.mime_type = $mime_type,
                    source.header = $header
                MERGE (graph_plan)-[:HAS_SOURCE]->(source)
                """,
                {"file_path": source.file_path, "mime_type": source.mime_type, "header": source.header}
            )
        # Add entities and their rules
        for entity in graph_plan.entities.values():
            tx.run("""
                MATCH (graph_plan:GraphPlan {id: $graph_plan_id})
                MERGE (entity:EntityPlan {id: $id})
                SET entity.name = $name,
                    entity.description = $description,
                    entity.property_keys = $property_keys
                MERGE (graph_plan)-[:HAS_ENTITY]->(entity)
                """,
                {"graph_plan_id": graph_plan.id, "id": entity.id, "name": entity.name, "description": entity.description, "property_keys": entity.property_keys}
            )
            for rule in entity.rules:

                rule_label = "Construction" if rule.kind == RuleKind.CONSTRUCTION else "Retrieval"
                # Create the rule with appropriate label
                if rule.kind == RuleKind.CONSTRUCTION:
                    tx.run("""
                        MATCH (entity:EntityPlan {id: $entity_id})
                        MERGE (rule:Rule:Construction {id: $id})
                        SET rule.tool = $tool
                        MERGE (entity)-[:HAS_RULE]->(rule)
                        """,
                        {"entity_id": entity.id, "id": rule.id, "tool": rule.tool}
                    )
                else:
                    tx.run("""
                        MATCH (entity:EntityPlan {id: $entity_id})
                        MERGE (rule:Rule:Retrieval {id: $id})
                        SET rule.tool = $tool
                        MERGE (entity)-[:HAS_RULE]->(rule)
                        """,
                        {"entity_id": entity.id, "id": rule.id, "tool": rule.tool}
                    )
                
                # Store rule args as separate properties
                if rule.args:
                    args_params = {f"arg_{k}": v for k, v in rule.args.items()}
                    args_set_clause = ", ".join([f"rule.{k} = ${k}" for k in args_params.keys()])
                    tx.run(f"""
                        MATCH (rule:Rule {{id: $id}})
                        SET {args_set_clause}
                        """,
                        {"id": rule.id, **args_params}
                )
        # Add relations and their rules
        for relation in graph_plan.relations.values():
            tx.run("""
                MATCH (graph_plan:GraphPlan {id: $graph_plan_id})
                MERGE (relation:RelationPlan {id: $id})
                SET relation.name = $name,
                    relation.description = $description,
                    relation.property_keys = $property_keys
                MERGE (graph_plan)-[:HAS_RELATION]->(relation)
                
                WITH relation
                MATCH (from_entity:EntityPlan {id: $from_entity_id})
                MATCH (to_entity:EntityPlan {id: $to_entity_id})
                MERGE (relation)-[:FROM_ENTITY]->(from_entity)
                MERGE (relation)-[:TO_ENTITY]->(to_entity)
                """,
                {"graph_plan_id": graph_plan.id, "id": relation.id, "name": relation.name, "description": relation.description, "property_keys": relation.property_keys, "from_entity_id": relation.from_entity.id, "to_entity_id": relation.to_entity.id}
            )
            for rule in relation.rules:
                rule_label = "Construction" if rule.kind == RuleKind.CONSTRUCTION else "Retrieval"
                # Create the rule with appropriate label
                if rule.kind == RuleKind.CONSTRUCTION:
                    tx.run("""
                        MATCH (relation:RelationPlan {id: $relation_id})
                        MERGE (rule:Rule:Construction {id: $id})
                        SET rule.tool = $tool
                        MERGE (relation)-[:HAS_RULE]->(rule)
                        """,
                        {"relation_id": relation.id, "id": rule.id, "tool": rule.tool}
                    )
                else:
                    tx.run("""
                        MATCH (relation:RelationPlan {id: $relation_id})
                        MERGE (rule:Rule:Retrieval {id: $id})
                        SET rule.tool = $tool
                        MERGE (relation)-[:HAS_RULE]->(rule)
                        """,
                        {"relation_id": relation.id, "id": rule.id, "tool": rule.tool}
                    )
                
                # Store rule args as separate properties
                if rule.args:
                    args_params = {f"arg_{k}": v for k, v in rule.args.items()}
                    args_set_clause = ", ".join([f"rule.{k} = ${k}" for k in args_params.keys()])
                    tx.run(f"""
                        MATCH (rule:Rule {{id: $id}})
                        SET {args_set_clause}
                        """,
                        {"id": rule.id, **args_params}
                )
        

    with graphdb.get_driver().session() as session:
        session.execute_write(store_graph_plan_tx, graph_plan)
        

        

def retrieve_graph_plan(id: str) -> Optional[GraphPlan]:
    """Retrieve a graph plan from the property graph.
    
    Args:
        id: The ID of the graph plan to retrieve
        
    Returns:
        The retrieved GraphPlan or None if not found
    """
    def retrieve_graph_plan_tx(tx, graph_plan_id: str) -> Optional[Dict]:
        # Retrieve the GraphPlan node
        result = tx.run("""
            MATCH (gp:GraphPlan {id: $id})
            RETURN gp {.id, .name, .description} as graph_plan
            """,
            {"id": graph_plan_id}
        )
        record = result.single()
        if not record:
            return None
            
        graph_plan_data = record["graph_plan"]
        
        # Retrieve FileSource nodes
        sources_result = tx.run("""
            MATCH (gp:GraphPlan {id: $id})-[:HAS_SOURCE]->(s:FileSource)
            RETURN s {.file_path, .mime_type, .header} as source
            """,
            {"id": graph_plan_id}
        )
        sources = {}
        for record in sources_result:
            source_data = record["source"]
            source = FileSource(
                file_path=source_data["file_path"],
                mime_type=source_data.get("mime_type", ""),
                header=source_data.get("header", [])
            )
            sources[source.file_path] = source
            
        # Retrieve EntityPlan nodes and their rules
        entities_result = tx.run("""
            MATCH (gp:GraphPlan {id: $id})-[:HAS_ENTITY]->(e:EntityPlan)
            RETURN e {.id, .name, .description, .property_keys} as entity
            """,
            {"id": graph_plan_id}
        )
        entities = {}
        for record in entities_result:
            entity_data = record["entity"]
            entity = EntityPlan(
                id=entity_data["id"],
                name=entity_data["name"],
                description=entity_data.get("description", ""),
                property_keys=entity_data.get("property_keys", [])
            )
            
            # Get rules for this entity
            rules_result = tx.run("""
                MATCH (e:EntityPlan {id: $id})-[:HAS_RULE]->(r:Rule)
                RETURN r {.id, .tool, .*} as rule,
                       labels(r) as labels
                """,
                {"id": entity_data["id"]}
            )
            
            for rule_record in rules_result:
                rule_data = rule_record["rule"]
                labels = rule_record["labels"]
                
                # Determine rule kind based on labels
                kind = RuleKind.CONSTRUCTION if "Construction" in labels else RuleKind.RETRIEVAL
                
                # Extract args (all properties except id and tool)
                args = {k: v for k, v in rule_data.items() if k not in ["id", "tool"]}
                
                rule = Rule(
                    id=rule_data["id"],
                    kind=kind,
                    tool=rule_data["tool"],
                    args=args
                )
                entity.rules.append(rule)
                
            entities[entity.id] = entity
            
        # Retrieve RelationPlan nodes and their rules
        relations_result = tx.run("""
            MATCH (gp:GraphPlan {id: $id})-[:HAS_RELATION]->(r:RelationPlan)
            OPTIONAL MATCH (r)-[:FROM_ENTITY]->(from_entity:EntityPlan)
            OPTIONAL MATCH (r)-[:TO_ENTITY]->(to_entity:EntityPlan)
            RETURN r {.id, .name, .description, .property_keys} as relation,
                   from_entity.id as from_entity_id,
                   to_entity.id as to_entity_id
            """,
            {"id": graph_plan_id}
        )
        relations = {}
        
        # We need to process relations after all entities are loaded
        relation_data_list = []
        for record in relations_result:
            relation_data_list.append({
                "relation": record["relation"],
                "from_entity_id": record["from_entity_id"],
                "to_entity_id": record["to_entity_id"]
            })
            
        # Now process relations after entities are loaded
        for data in relation_data_list:
            relation_data = data["relation"]
            from_entity_id = data["from_entity_id"]
            to_entity_id = data["to_entity_id"]
            
            # For now, create placeholder entities if they don't exist
            # In a real implementation, you'd want to handle this more gracefully
            from_entity = entities.get(from_entity_id) if from_entity_id else EntityPlan(name="Unknown")
            to_entity = entities.get(to_entity_id) if to_entity_id else EntityPlan(name="Unknown")
            
            relation = RelationPlan(
                id=relation_data["id"],
                name=relation_data["name"],
                description=relation_data.get("description", ""),
                property_keys=relation_data.get("property_keys", []),
                from_entity=from_entity,
                to_entity=to_entity
            )
            
            # Get rules for this relation
            rules_result = tx.run("""
                MATCH (r:RelationPlan {id: $id})-[:HAS_RULE]->(rule:Rule)
                RETURN rule {.id, .tool, .*} as rule,
                       labels(rule) as labels
                """,
                {"id": relation_data["id"]}
            )
            
            for rule_record in rules_result:
                rule_data = rule_record["rule"]
                labels = rule_record["labels"]
                
                # Determine rule kind based on labels
                kind = RuleKind.CONSTRUCTION if "Construction" in labels else RuleKind.RETRIEVAL
                
                # Extract args (all properties except id and tool)
                args = {k: v for k, v in rule_data.items() if k not in ["id", "tool"]}
                
                rule = Rule(
                    id=rule_data["id"],
                    kind=kind,
                    tool=rule_data["tool"],
                    args=args
                )
                relation.rules.append(rule)
                
            relations[relation.id] = relation
        
        # Return all the data needed to construct a GraphPlan
        return {
            "graph_plan": graph_plan_data,
            "sources": sources,
            "entities": entities,
            "relations": relations
        }
    
    # Execute the transaction
    with graphdb.get_driver().session() as session:
        data = session.execute_read(retrieve_graph_plan_tx, id)
        if not data:
            return None
        
        # Create the GraphPlan
        graph_plan = GraphPlan(
            id=data["graph_plan"]["id"],
            name=data["graph_plan"]["name"],
            description=data["graph_plan"].get("description", "")
        )
        
        # Add sources
        for source in data["sources"].values():
            graph_plan.sources[source.file_path] = source
            
        # Add entities
        for entity in data["entities"].values():
            graph_plan.entities[entity.id] = entity
            
        # Add relations
        for relation in data["relations"].values():
            graph_plan.relations[relation.id] = relation
            
        return graph_plan
