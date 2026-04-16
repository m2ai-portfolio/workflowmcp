
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
WorkflowMCP is an MCP server enabling declarative definition, execution, and monitoring of multi-agent workflows via YAML. It integrates with Claude Code for agent skills and supports Copilot SDK extensibility, targeting solo AI developers who need to prototype agent-based systems without procedural glue.

Example usage:
```
$ workflow-mcp parse --file example.yaml
{"name": "example_workflow", "steps": [{"agent": "researcher", "tool": null, "depends_on": []}, {"agent": "writer", "tool": "summarizer", "depends_on": [0]}]}
```

## Problem
Solo developers struggle to orchestrate multi-agent agents because they must write procedural code for each step, making workflows hard to visualize, modify, and share. Current methods involve ad-hoc scripts or complex orchestration tools that are overkill for solo use.

## Features
| Feature | Description |
|---------|-------------|
| Declarative YAML Workflow Definition | Define multi-agent workflows in YAML specifying agents, tools, and step dependencies without writing imperative code. |
| Workflow Validation and Parsing | Parse YAML workflows and validate against the DSL, generating a directed acyclic graph (DAG) for static analysis. |
| Real-time Execution Monitoring | Monitor agent runs with metrics collection, exporting to Prometheus format or logging to stdout for observability. |
| Workflow Visualization | Generate Mermaid diagrams to visualize workflow dependencies and structure for debugging and sharing. |
| Copilot SDK Integration | Dynamically load and execute custom agent skills via the Copilot SDK entrypoint for language-model-powered tools. |
| Skill Management | List available skills and run them with defined input/output contracts using the Copilot SDK CLI. |

## Quick Start
1. Clone the repository:  
   `git clone https://github.com/m2ai-portfolio/workflow-mcp.git`
2. Install dependencies:  
   `cd workflow-mcp && pip install -e .`
3. Parse an example workflow:  
   `workflow-mcp parse --file example.yaml`

## Examples
**Basic workflow parsing**  
```
$ workflow-mcp parse --file example.yaml
{"name": "example_workflow", "steps": [{"agent": "researcher", "tool": null, "depends_on": []}, {"agent": "writer", "tool": "summarizer", "depends_on": [0]}, {"agent": "reviewer", "tool": null, "depends_on": [1]}]}
```

**Real-time monitoring in Prometheus format**  
```
$ workflow-mcp monitor --workflow example --format prometheus
# HELP workflow_steps_total Total number of workflow steps executed
# TYPE workflow_steps_total counter
workflow_steps_total{workflow="example",status="success"} 3
```

**Loading and running a Copilot skill**  
```
$ copilot_sdk load_skill --name summarizer
Skill loaded: summarizer (handle: skill_123)
$ copilot_sdk run_skill --handle skill_123 --input '{"text":"The quick brown fox jumps over the lazy dog."}'
{"summary": "Fox jumps over dog."}
```

## File Structure
```
WorkflowMCP: Declarative Agent Orchestration/
  workflow_mcp/          # Core source code
    __init__.py
    cli.py               # Main CLI entrypoint
    core.py              # Workflow execution engine
    models/              # Data models
      __init__.py
      agent.py           # AgentModel definition
      workflow.py        # WorkflowModel and StepModel
    monitoring/          # Observability components
      __init__.py
      observer.py        # Metrics collection and export
    sdk/                 # Copilot SDK integration
      __init__.py
      cli.py             # SDK command-line interface
      loader.py          # Dynamic skill loading
      skills/            # Built-in agent skills
        __init__.py
        planner.py
        summarizer.py
        translator.py
    tests/               # Test suite
      __init__.py
      conftest.py
      test_monitoring.py
      test_sdk.py
      test_workflow.py
  pyproject.toml         # Project configuration and dependencies
  example.yaml           # Sample workflow definition
  bad.yaml               # Invalid workflow for validation testing
  init.sh                # Environment setup script
```

## Tech Stack
| Technology | Purpose |
|------------|---------|
| Python 3.11+ | Core language runtime |
| click | CLI framework for command interfaces |
| pytest | Testing framework for validation |

## Contributing
Fork the repository, create a feature branch, make changes with tests, and submit a pull request.

## License
MIT

## Author
Matthew Snow -- [M2AI](https://m2ai.co) | [@m2ai-portfolio](https://github.com/m2ai-portfolio)