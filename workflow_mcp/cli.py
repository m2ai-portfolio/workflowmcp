"""Command-line interface for WorkflowMCP."""

import json
import sys
from pathlib import Path
import click

from .core import parse_workflow, validate_workflow, visualize_workflow


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """WorkflowMCP: Declarative Agent Orchestration via YAML."""
    pass


@cli.command()
@click.option("--file", "-f", required=True, help="Path to the workflow YAML file")
def parse(file: str):
    """Parse a workflow YAML file and output JSON DAG representation."""
    try:
        dag = parse_workflow(file)
        output = json.dumps(dag, indent=2)
        click.echo(output)
        sys.exit(0)
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error parsing workflow: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--file", "-f", required=True, help="Path to the workflow YAML file")
def validate(file: str):
    """Validate a workflow YAML file."""
    is_valid, errors = validate_workflow(file)

    if is_valid:
        click.echo("Workflow is valid")
        sys.exit(0)
    else:
        click.echo("Workflow validation failed:", err=True)
        for error in errors:
            click.echo(f"  - {error}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--file", "-f", required=True, help="Path to the workflow YAML file")
@click.option("--output", "-o", default="workflow.mmd", help="Output file path for Mermaid diagram")
def visualize(file: str, output: str):
    """Generate a Mermaid diagram visualization of the workflow."""
    try:
        mermaid = visualize_workflow(file)

        # Write to file
        output_path = Path(output)
        with open(output_path, 'w') as f:
            f.write(mermaid)

        click.echo(f"Mermaid diagram saved to {output}")

        # Try to render to PNG if mmdc is available
        try:
            import subprocess
            result = subprocess.run(
                ["mmdc", "-i", str(output_path), "-o", str(output_path.with_suffix(".png"))],
                capture_output=True,
                timeout=10
            )
            if result.returncode == 0:
                click.echo(f"PNG diagram saved to {output_path.with_suffix('.png')}")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            # mmdc not available, that's ok
            pass

        sys.exit(0)
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error generating visualization: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
