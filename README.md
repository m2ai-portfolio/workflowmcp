

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
WorkflowMCP is an MCP server that lets you declare multi‑agent workflows in YAML, execute them via Claude Code agent skills, and monitor runs in real time. It targets solo AI developers who want to prototype agent‑based systems without writing procedural glue.  
Example:
```
$ workflow-mcp parse --file example.yaml
{
  "name": "example",
  "steps": [
    {"id":0,"agent":"researcher","tool":null,"depends_on":[]},
    {"id":1,"agent":"summarizer","tool":null,"depends_on":[0]},
    {"id":2,"agent":"translator","tool":null,"depends_on":[1]}
  ]
}
```

## Problem
Solo developers struggle to orchestrate multi-agent agents because they must write procedural code for each step, making workflows hard to visualize, modify, and share. Current methods involve ad-hoc scripts or complex orchestration tools that are overkill for solo use.

## Features
| Feature | Description |
|---------|-------------|
| Declarative YAML Workflow Definition | Define agents, tools, and step dependencies in YAML; the engine builds a directed acyclic graph (DAG) for execution. |
| Real‑time Execution Monitoring | Subscribe to Claude Code execution streams, record timestamps/token usage, and export metrics in Prometheus format or JSON lines. |
| Extensible SDK Integration | Load custom agent skills through the Copilot SDK entrypoint; supports dynamic loading from local files or git repositories. |
| Workflow Validation & Visualization | Validate YAML against the workflow DSL and generate Mermaid diagrams for quick inspection. |
| CLI‑driven Orchestration | Simple commands to parse, validate, run, and monitor workflows without writing any procedural code. |

## Quick Start
1. Clone the repository:  
   `git clone https://github.com/your-org/workflow-mcp.git`
2. Change directory:  
   `cd workflow-mcp`
3. Install in development mode:  
   `pip install -e .`
4. Run a basic parse command:  
   `workflow-mcp parse --file example.yaml`
5. (Optional) Start a Prometheus metrics endpoint:  
   `workflow-mcp monitor --workflow example --format prometheus`

## Examples
**Example 1: Parsing a workflow**  
Command:  
```
workflow-mcp parse --file example.yaml
```
Output:  
```
{
  "name": "example",
  "steps": [
    {"id":0,"agent":"researcher","tool":null,"depends_on":[]},
    {"id":1,"agent":"summarizer","tool":null,"depends_on":[0]},
    {"id":2,"agent":"translator","tool":null,"depends_on":[1]}
  ]
}
```

**Example 2: Monitoring with Prometheus format**  
Command:  
```
workflow-mcp monitor --workflow example --format prometheus
```
Output:  
```
# HELP workflow_steps_total Total number of workflow steps executed
# TYPE workflow_steps_total counter
workflow_steps_total{workflow="example",status="success"} 3
```

**Example 3: Running a Copilot skill**  
Command:  
```
copilot_sdk run_skill --handle summarizer --input '{"text":"The quick brown fox jumps over the lazy dog."}'
```
Output:  
```
{"summary":"Fox jumps over dog."}
```

## File Structure
```
WorkflowMCP: Declarative Agent Orchestration/
  workflow_mcp/                  # Core source package
    cli.py                       # CLI entry point (workflow-mcp)
    core.py                      # Workflow engine and DAG builder
    models/                      # Pydantic models for workflow and agent
      __init__.py
      workflow.py
      agent.py
    monitoring/                  # Real‑time observer and metrics exporter
      __init__.py
      observer.py
    sdk/                         # Copilot SDK integration
      __init__.py
      loader.py
      skills/                    # Example agent skills
        __init__.py
        summarizer.py
        translator.py
        planner.py
    tests/                       # Unit test suite
      __init__.py
      test_workflow.py
      test_agent.py
      test_monitoring.py
      test_sdk.py
  assets/                        # Diagram assets
    infographic.png
  screenshots/                   # Demo screenshots (selected)
  example.yaml                   # Sample workflow definition
  bad.yaml                       # Invalid workflow for validation tests
  pyproject.toml                 # Project metadata and dependencies
  README.md
  LICENSE
```

## Tech Stack
| Technology | Purpose |
|------------|---------|
| Python 3.11+ | Core language |
| click | Building the command‑line interface |
| pytest | Running unit tests |

## Contributing
Fork the repository, create a feature branch.  
Make your changes, add tests, and ensure the test suite passes.  
Submit a pull request with a clear description of your work.

## License
MIT

## Author
Matthew Snow -- [M2AI](https://m2ai.co) | [@m2ai-portfolio](https://github.com/m2ai-portfolio)