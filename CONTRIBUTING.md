# Contributing to Agentic-KG

Thank you for your interest in contributing to the Agentic-KG project! This document outlines the guidelines for contributing to this project.

## Commit Message Format

We follow a structured commit message format to maintain a clear and consistent commit history. Each commit message should follow this pattern:

```
(component) Concise description of the change
```

Where:
- `component` identifies the part of the codebase being modified
- The description should be clear, concise, and written in the imperative mood (e.g., "Add feature" not "Added feature")

### Components

Use one of the following components:

- `file_tools`: Changes to file manipulation tools
- `agent`: Changes to agent implementation
- `kg`: Changes to knowledge graph functionality
- `dataprep`: Changes to data preparation
- `docs`: Documentation changes
- `tests`: Test-related changes
- `infra`: Infrastructure or build system changes
- `misc`: Miscellaneous changes

### Examples

Good commit messages:
- `(file_tools) Add search functionality for markdown files`
- `(agent) Improve error handling in dataprep agent`
- `(tests) Add comprehensive tests for search_file function`

Poor commit messages:
- `Fixed bug` (too vague, missing component)
- `(file_tools) Added some stuff and fixed other things` (not specific enough)
- `WIP` (uninformative)

## Pull Request Process

1. Ensure your code passes all tests
2. Update documentation as necessary
3. Follow the commit message format for all commits
4. Submit your pull request with a clear description of the changes

## Code Style

- Follow PEP 8 guidelines for Python code
- Use meaningful variable and function names
- Include docstrings for all functions, classes, and modules
- Write clear comments for complex logic

## Testing

- Add tests for new functionality
- Ensure all tests pass before submitting a pull request
- Maintain or improve code coverage

Thank you for helping make this project better!
