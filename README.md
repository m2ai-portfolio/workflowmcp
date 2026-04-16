

<p align="center">
  <img src="assets/infographic.png" alt="WorkflowMCP: Declarative Agent Orchestration" width="800">
</p>

<h3 align="center">An MCP server that provides a declarative way to define, run, and monitor multi-agent workflows using YAML. Integrates with Claude Code for agent skills and supports embedding agentic execution layers like Copilot SDK for extensibility.</h3>

<p align="center">
  <a href="#quick-start">Quick Start</a> &bull;
  <a href="#features">Features</a> &bull;
  <a href="#examples">Examples</a> &bull;
  <a href="#contributing">Contributing</a>
</p>

## What is this?
WorkflowMCP is an MCP server that lets solo AI developers declaratively define multi‑agent workflows in YAML, execute them with Claude Code skills, and monitor progress in real time. It removes the need for procedural glue code, making workflows easy to visualize, modify, and share.

```
$ workflow-mcp parse --file example.yaml
{
  "name": "example",
  "steps": [
    {"id":0,"agent":"researcher","tool":null,"depends_on":[]},
    {"id":1,"agent":"writer","tool":"summarizer","depends_on":[0]},
    {"id":2,"agent":"reviewer","tool":null,"depends_on":[1]}
  ]
}
```

## Problem
Solo developers struggle to orchestrate multi-agent agents because they must write procedural code for each step, making workflows hard to visualize, modify, and share. Current methods involve ad-hoc scripts or complex orchestration tools that are overkill for solo use.

## Features
| Feature | Description |
|---------|-------------|
| Declarative YAML Workflow Definition | Define agents, tools, and step dependencies in YAML; the CLI parses and validates the schema, producing a DAG for execution. |
| Real‑time Agent Execution Monitoring | Subscribe to Claude Code execution streams via WebSocket, record timestamps, token usage, and status, and export metrics in Prometheus format. |
| Extensible SDK Integration (Copilot) | Load custom agent skills locally or from git via the Copilot SDK entrypoint; skills follow a simple dict‑in/dict‑out API. |
| Workflow Validation & Visualization | Validate YAML against the workflow DSL and generate Mermaid diagrams for quick inspection. |
| CLI‑Driven Workflow Lifecycle | Commands `parse`, `validate`, `monitor`, and `visualize` cover the full workflow lifecycle from definition to observability. |
| Built‑in Skill Examples | Includes planner, summarizer, and translator skills to demonstrate SDK usage out‑of‑the‑box. |

## Quick Start
1. Clone the repository:  
   `git clone https://github.com/yourorg/workflow-mcp.git`
2. Change into the project directory:  
   `cd workflow-mcp`
3. Install in editable mode:  
   `pip install -e .`
4. Verify the setup by parsing the sample workflow:  
   `workflow-mcp parse --file example.yaml`

## Examples
**Basic workflow parsing**  
Parse a sample workflow and view its directed acyclic graph representation.  
```
$ workflow-mcp parse --file example.yaml
{
  "name": "example",
  "steps": [
    {"id":0,"agent":"researcher","tool":null,"depends_on":[]},
    {"id":1,"agent":"writer","tool":"summarizer","depends_on":[0]},
    {"id":2,"agent":"reviewer","tool":null,"depends_on":[1]}
  ]
}
```

**Real‑time monitoring with Prometheus output**  
Run a workflow and expose metrics for scraping.  
```
$ workflow-mcp monitor --workflow example --format prometheus
# HELP workflow_steps_total Total number of workflow steps executed
# TYPE workflow_steps_total counter
workflow_steps_total 3
```

**Using the Copilot SDK to list and run a skill**  
Load a summarizer skill and run it on input text.  
```
$ copilot_sdk list_skills
planner
summarizer
translator
$ copilot_sdk run_skill --handle summarizer --input "{\"text\":\"The quick brown fox jumps over the lazy dog.\"}"
{"summary":"Fox jumps over lazy dog."}
```

## File Structure
```
WorkflowMCP: Declarative Agent Orchestration/
├── workflow_mcp/               # Source code
│   ├── __init__.py
│   ├── cli.py                  # Main CLI entry point (workflow-mcp)
│   ├── core.py                 # Core orchestration logic
│   ├── models/
│   │   ├── __init__.py
│   │   ├── workflow.py         # WorkflowModel definition
│   │   └── agent.py            # AgentModel definition
│   ├── monitoring/
│   │   ├── __init__.py
│   │   └── observer.py         # Real‑time metrics observer
│   ├── sdk/
│   │   ├── __init__.py
│   │   ├── cli.py              # Copilot SDK CLI (copilot_sdk)
│   │   ├── loader.py           # Skill loading utilities
│   │   └── skills/             # Built‑in skills
│   │       ├── __init__.py
│   │       ├── planner.py
│   │       ├── summarizer.py
│   │       └── translator.py
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_workflow.py
│       ├── test_agent.py
│       └── test_sdk.py
├── assets/
│   └── infographic.png
├── example.yaml                # Sample workflow definition
├── bad.yaml                    # Invalid workflow for validation tests
├── pyproject.toml              # Project configuration and dependencies
├── init.sh                     # Setup script for development
└── README.md
```

## Tech Stack
| Technology | Purpose |
|------------|---------|
| Python 3.11+ | Core language |
| click | Building the CLI interface |
| pytest | Unit and integration testing |
| pyyaml | Parsing YAML workflow definitions |
| prometheus_client | Exporting metrics in Prometheus format |
| websockets | Subscribing to Claude Code execution streams |

## Contributing
Fork the repository.  
Make your changes.  
Run the test suite.  
Submit a pull request.

## License
MIT

## Author
Matthew Snow -- [M2AI](https://m2ai.co) | [@m2ai-portfolio](https://github.com/m2ai-portfolio)