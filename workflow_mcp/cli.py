"""CLI commands for WorkflowMCP."""

import json
import sys
import click

from workflow_mcp.core import (
    parse_yaml,
    validate_workflow,
    generate_dag,
    generate_mermaid,
    WorkflowParseError,
)


@click.group()
def cli():
    """WorkflowMCP: Declarative Agent Orchestration."""
    pass


@cli.command()
@click.option('--file', required=True, help='Path to workflow YAML file')
def parse(file):
    """Parse a workflow file and output JSON DAG representation."""
    try:
        workflow = parse_yaml(file)
        dag = generate_dag(workflow)
        click.echo(json.dumps(dag, indent=2))
        sys.exit(0)
    except WorkflowParseError as e:
        click.echo(f"ERROR: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"ERROR: Unexpected error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--file', required=True, help='Path to workflow YAML file')
def validate(file):
    """Validate a workflow file for correctness."""
    try:
        workflow = parse_yaml(file)
        is_valid, errors = validate_workflow(workflow)

        if is_valid:
            click.echo("Workflow is valid")
            sys.exit(0)
        else:
            for error in errors:
                click.echo(f"ERROR: {error}", err=True)
            sys.exit(1)

    except WorkflowParseError as e:
        click.echo(f"ERROR: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"ERROR: Unexpected error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--file', required=True, help='Path to workflow YAML file')
@click.option('--output', default='out.mmd', help='Output file for Mermaid diagram')
def visualize(file, output):
    """Generate a Mermaid diagram from a workflow file."""
    try:
        workflow = parse_yaml(file)
        is_valid, errors = validate_workflow(workflow)

        if not is_valid:
            click.echo("WARNING: Workflow has validation errors:", err=True)
            for error in errors:
                click.echo(f"  - {error}", err=True)

        mermaid = generate_mermaid(workflow)

        with open(output, 'w') as f:
            f.write(mermaid)

        click.echo(f"Mermaid diagram saved to {output}")
        sys.exit(0)

    except WorkflowParseError as e:
        click.echo(f"ERROR: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"ERROR: Unexpected error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
