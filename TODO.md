# Project Todo List

## full_workflow coordinator
- [ ] Add a sub-agent for importing unstructured data sources (unstructured_data_agent)

## unstructured_data_agent sub-agent
- [ ] write a prompt that describes how to load, chunk and extract entities and relations from unstructured data sources
- [ ] create a code tool for chunking
- [ ] create an agent tool for entity extraction
- [ ] create an agent tool for relation extraction
- [ ] create a critic agent to review and rate the relevance of extracted entities and relations, taking into account existing schema and user goals
- [ ] implement metadata extraction for documents
- [ ] add incremental update handling for existing entities

## file_tools
- [x] include markdown in file listing
- [x] add search_csv tool for searching csv files for rows that match a given value using a simple grep-like, line-oriented function
- [x] add search_csv to the dataprep_agent and try it out using the agent
- [x] add search_markdown tool for searching markdown files for a line that contains a given value using a simple grep-like query
- [x] add search_markdown to the dataprep_agent and try it out using the agent
- [x] simplify the search tools by using a single tool for any text file (which includes csv) that runs like grep, returning an array of lines that match the search query.

## graph_plan data structure
- [ ] Add support for markdown construction rule
- [ ] Add schema validation for extracted entities/relations

---

Low priority TODO categories

## Integration
- [ ] Add error handling between sub-agents
- [ ] Add tests for the full unstructured data pipeline
- [ ] Document the expected data flow between components

## Performance
- [ ] Add benchmarks for text processing throughput
- [ ] Implement caching for expensive operations

## Error Handling & Validation
- [ ] Add validation for extracted entities/relations
- [ ] Implement retry logic for transient failures
- [ ] Add comprehensive error handling for Neo4j operations

## Documentation
- [ ] Document the unstructured data processing pipeline
- [ ] Add examples for different data sources
- [ ] Create API documentation for new components

## Testing
- [ ] Add unit tests for new components
- [ ] Implement integration tests for the full workflow
- [ ] Add performance tests for large documents

## Technical Debt
- [ ] Review and update dependencies
- [ ] Add type hints to new code
- [ ] Standardize error messages across modules

---

## Code TODOs

Run `grep -r "TODO:" .` to find all TODOs in the codebase.

Add new TODOs in the code using this format:
```python
# TODO: [short description] - [priority: high/medium/low] - [estimated time]
# Example:
# TODO: Add input validation for user_id - priority: high - 1h
```
