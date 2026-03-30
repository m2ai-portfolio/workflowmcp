

# WorkflowMCP: Declarative Agent Orchestration  
  

## Overview  
WorkflowMCP is an MCP server that enables declarative definition, execution, and monitoring of multi‑agent workflows via YAML. It integrates with Claude Code and supports Copilot SDK extensions, allowing solo AI developers to quickly prototype and test agent‑based systems without writing procedural glue.

## Problem Statement  
Solo developers struggle to orchestrate multi‑agent agents because they must write procedural code for each step, making workflows hard to visualize, modify, and share. Current methods rely on ad‑hoc scripts or complex orchestration tools that are overkill for solo use.

## Features  
- Declarative YAML workflow definition  
- Real‑time agent execution monitoring  
- Extensible SDK integration (Copilot)  

## Tech Stack  
- Python 3.11+  
- click (CLI framework)  
- pytest (testing)  

## Quick Start / Installation  
1. Clone the repository: `git clone https://github.com/your-org/workflow-mcp.git`  
2. Create a virtual environment: `python -m venv venv`  
3. Activate the environment: `source venv/bin/activate`  
4. Install dependencies: `pip install -r requirements.txt`  
5. Run the MCP server: `workflow-mcp start --port 8000`  

## Usage  
- Define a workflow in YAML (see `example.yaml`)  
- Start the server and monitor runs via the CLI: `workflow-mcp monitor --workflow example`  
- Load custom agent skills with Copilot SDK: `copilot_sdk load_skill --name summarizer`  

## Architecture  
The WorkflowMCP server consists of a YAML‑driven MCP core, a Claude Code observer for real‑time execution streaming, and a Copilot SDK plug‑in system for extensible agent skills. The server exposes a REST/WebSocket API for external interaction and stores workflow state in memory for fast lookup.  

## License  
MIT  

---  
*Generated from the official app specification.*