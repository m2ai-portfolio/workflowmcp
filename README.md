

# WorkflowMCP: Declarative Agent Orchestration ![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg) ![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)


## Overview
WorkflowMCP is an MCP server that enables declarative definition, execution, and monitoring of multi‑agent workflows via YAML. It integrates with Claude Code for agent reasoning and supports Copilot SDK extensions for pluggable skills, allowing solo AI developers to prototype and test agent‑based systems without writing procedural glue.

## Problem Statement
Solo AI developers struggle to orchestrate multi‑agent agents because they must write procedural code for each step, making workflows hard to visualize, modify, and share. Existing solutions rely on ad‑hoc scripts or complex orchestration tools that are overkill for solo use, slowing down iteration and collaboration.

## Features
- **Declarative YAML Workflow**: Define agents, tools, and step dependencies in YAML; the server builds a DAG and handles execution automatically.  
- **Real‑time Monitoring**: Subscribe to Claude Code execution streams via WebSocket, collect metrics, and emit Prometheus‑compatible events for debugging and observability.  
- **Copilot SDK Integration**: Load custom agent skills at runtime from local filesystem or Git, exposing a typed API for skill invocation.  
- **Static Analysis & Visualization**: Generate Mermaid diagrams of workflow DAGs for design‑time inspection.  
- **Extensible Architecture**: Plugin‑based MCP core lets you add new transports, storage backends, or UI layers without touching the core.

## Tech Stack
- **Language**: Python 3.11+  
- **Framework**: FastAPI (for HTTP/MCP endpoints) + Pydantic (settings validation)  
- **Library**: PyYAML (YAML parsing), Click (CLI), Prometheus‑client (metrics), WebSocket‑client (monitoring), Jinja2 (template rendering)  
- **Testing**: Pytest, Hypothesis  
- **DevOps**: Docker, GitHub Actions  

## Quick Start / Installation
```bash
# Clone the repository
git clone https://github.com/your-org/workflow-mcp.git
cd workflow-mcp

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set configuration (optional)
cp example.yaml workflow_mcp/config.yaml

# Run the MCP server
workflow-mcp start --port 8000

# Run the CLI workflow parser
workflow-mcp parse --file examples/simple.yaml
```
*Default configuration assumes TCP port 8000, log level INFO, and looks for YAML files under `workflow_mcp/config/`.*

## Usage
```bash
# Validate a workflow definition
workflow-mcp validate --file my_workflow.yaml

# Visualize a workflow as Mermaid
workflow-mcp visualize --file my_workflow.yaml --out diagram.png

# Monitor a running workflow (Prometheus format)
workflow-mcp monitor --workflow my_workflow --format prometheus

# Load a Copilot skill from Git
copilot_sdk load_skill --name summarizer --repo https://github.com/your-org/skills.git --branch main

# Invoke a loaded skill
copilot_sdk run_skill --handle h_123 --input '{"text":"Translate this to French."}'
```
*See `workflow-mcp --help` and `copilot_sdk --help` for full command references.*

## Architecture
```
workflow_mcp/
├── workflow_mcp/
│   ├── __init__.py
│   ├── core.py          # MCP server lifecycle, settings, transport
│   ├── cli.py             # Typer‑based command line interface
│   ├── models/
│   │   ├── workflow.py   # Pydantic models for Workflow, Step, Agent
│   │   └── agent.py     # Pydantic models for Agent, Skill, Config
│   ├── monitoring/
│   │   ├── __init__.py
│   │   └── observer.py   # WebSocket observer, Prometheus exporter, metric collector
│   ├── sdk/
│   │   ├── __init__.py
│   │   └── loader.py      # Copilot SDK skill loader (filesystem/git, API registration)
│   └── tests/
│   │   ├── test_workflow.py
│   │   ├── test_agent.py
│   │   └── test_sdk.py
├── pyproject.toml
```
*The MCP server exposes a JSON‑RPC compatible endpoint at `/mcp/v1`. The CLI communicates via JSON over stdin/stdout. Skill modules are plain Python packages with an `entrypoint` named `copilot_sdk.load_skill`.*

## License
MIT License

Copyright (c) 2025 WorkflowMCP Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGE OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.