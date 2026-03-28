# WorkflowMCP: Declarative Agent Orchestration

WorkflowMCP is a Python 3.11+ CLI tool that enables declarative agent orchestration via YAML workflows. It provides a structured approach to defining, managing, and executing complex agent-based workflows without requiring imperative code for orchestration logic.

## Tech Stack

- **Python 3.11+**: Core runtime
- **click**: CLI framework for command-line interface
- **pytest**: Testing framework for unit and integration tests
- **PyYAML**: YAML parsing for workflow definitions

## Features

- Declarative workflow definitions using YAML
- Built-in agent orchestration capabilities
- CLI tool for workflow execution and management
- Comprehensive test suite

## Project Structure

```
workflow-mcp/
├── README.md              # Project documentation
├── init.sh               # Development environment setup
├── .gitignore           # Git ignore rules
├── pyproject.toml       # Project metadata and dependencies
├── requirements.txt     # Python dependencies
├── src/
│   └── workflow_mcp/     # Main package
│       ├── __init__.py
│       ├── cli.py        # Click CLI commands
│       ├── workflow.py   # Workflow execution logic
│       └── parser.py     # YAML workflow parser
└── tests/
    ├── conftest.py      # Pytest configuration
    └── test_*.py        # Test modules
```

## Getting Started

### Development Setup

Run the initialization script to set up your development environment:

```bash
bash init.sh
```

This will:
- Create a Python virtual environment
- Install project dependencies (click, pytest, pyyaml)
- Prepare the environment for development

### Running Workflows

```bash
workflow-mcp run path/to/workflow.yaml
```

### Running Tests

```bash
pytest
```

## License

See LICENSE file for details.
