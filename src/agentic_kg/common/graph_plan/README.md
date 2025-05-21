# Graph Plan - how to build a knowledge graph from data files

This module defines a declarative structure called a "graph plan" for building a knowledge graph from prepared data files.

## From user goal to a graph plan

1. User goal, which will become the graph plan description
2. Data files, which will become file source in the graph plan
3. Graph plan, which starts with just a name, description and file sources
4. Entity and relation plans, which will be added to the graph plan
5. Construction rules, which will be added to the entity and relation plans

The resulting graph plan can then be used for constructing a graph.

## Overview of the process

To begin, the user must describe their goal, which can include details like:
- domain of interest, for example "a logistics graph of routes, shipments, and containers"
- scope of interest, for example "everything available" or "only within the US"
- how general or specific the graph should be, for example "very general" or "very specific"

A graph plan support knowledge graph construction through three phases:

1. Identify data sources
2. Design a data model
3. Construct the knowledge graph

## Identify data sources

The input to this phase is:
- the user's goal
- a directory of prepared data files

The output of the phase is:
- a list of data files that are relevant to the goal

The workflow follows these steps:
1. Analyze each file to determine if it is relevant to the user goal
    - consider file name, directory structure, and file content
2. Select the files that are relevant to the user goal
3. Suggest the files to the user, with an explanation of why each file is relevant
4. If the user approves, then finish the phase and return the list of files as the "approved files"
5. If the user rejects, then return to step 1 with the user's feedback. Possible feedback includes:
    - expanding the scope of relevant data
    - narrowing the scope of relevant data

## Design a data model

The input to this phase is:
- the user's goal
- the list of approved files

The output of the phase is:
- a graph plan with entities and relations along with construction rules

The workflow follows these steps:
1. Create a graph plan from the approved files, converting them into file sources
2. For each file source, determine how it can contribute to the graph. There are two main branches:
    - a. structured data - a CSV file
    - b. unstructured data - a markdown file
3. Add the resulting EntityPlan or RelationshipPlan to the GraphPlan
4. Return to 2 if there are more file sources to process

For structured data, the steps continue as follows:
1. Determine whether the data is a node or a relationship
    - consider file name, possible correlation with other file names
    - sample the contents to analyze the header and some row data
    - relationships typically have two id fields, both of which correlate to fields from other files (as happens in a join table)
2. Determine appropriate entity label or relationship type, as guided by the user goal
3. Add an EntityPlan or RelationshipPlan to the GraphPlan
4. Add construction rules to the EntityPlan or RelationshipPlan using an appropriate tool:
    - load_csv_nodes(file name, label, id field)
    - load_csv_relationships(file name, from_label, from_id_field, to_label, to_id_field, relationship_type)

For unstructured data, the steps continue as follows:
1. TBD. Finish structured flow first.


