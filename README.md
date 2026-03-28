# WorkflowMCP: Declarative Agent Orchestration

A Python 3.11+ CLI tool for declarative agent orchestration via YAML. WorkflowMCP enables seamless workflow definition, real-time execution monitoring, and extensible Copilot SDK integration.

## Tech Stack

- **Language:** Python 3.11+
- **CLI Framework:** click
- **Testing:** pytest
- **Package Management:** pip/setuptools

## Features

1. **YAML Workflow Definition & Parsing** - Define complex agent workflows declaratively using YAML files with full parsing and validation support
2. **Real-time Agent Execution Monitoring** - Monitor and track agent execution in real-time with comprehensive observability insights
3. **Extensible Copilot SDK Integration** - Integrate with Copilot SDK for enhanced capabilities and extensibility

## Setup Instructions

### Prerequisites
- Python 3.11 or higher
- pip package manager

### Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/workflow-mcp.git
cd workflow-mcp
```

2. Run the initialization script:
```bash
chmod +x init.sh
./init.sh
```

This will:
- Create a Python virtual environment
- Install project dependencies
- Verify the installation

3. Access the CLI:
```bash
python -m workflow_mcp --help
```

### Manual Setup

If you prefer to set up manually:

```bash
# Create virtual environment
python3.11 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .

# Verify installation
python -m workflow_mcp --help
```

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Project Structure

```
workflow_mcp/
├── __init__.py              # Package initialization
├── core.py                  # Core orchestration logic
├── cli.py                   # Command-line interface
├── models/
│   ├── workflow.py          # Workflow data models
│   └── agent.py             # Agent data models
├── monitoring/
│   └── observer.py          # Execution monitoring
├── sdk/
│   ├── __init__.py
│   └── loader.py            # SDK integration loader
├── tests/
│   ├── test_workflow.py
│   ├── test_agent.py
│   └── test_sdk.py
└── pyproject.toml           # Project configuration
```

## License

MIT
