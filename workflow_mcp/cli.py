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
from workflow_mcp.monitoring import WorkflowObserver


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


@cli.command()
@click.option('--workflow', required=True, help='Path to workflow YAML file')
@click.option('--format', type=click.Choice(['json', 'prometheus']), default='json', help='Output format (json or prometheus)')
@click.option('--test', is_flag=True, help='Test mode: simulate a failure')
def monitor(workflow, format, test):
    """Monitor workflow execution in real-time."""
    try:
        # Parse the workflow
        workflow_model = parse_yaml(workflow)

        # Validate the workflow
        is_valid, errors = validate_workflow(workflow_model)
        if not is_valid:
            for error in errors:
                click.echo(f"ERROR: {error}", err=True)
            sys.exit(1)

        # Create observer and execute workflow
        observer = WorkflowObserver(workflow_model, test_mode=test)

        try:
            metrics = observer.execute_and_monitor()

            # Output based on format
            if format == 'prometheus':
                click.echo(observer.format_prometheus_metrics())
            # For json format, events are already streamed during execution
            # Just need to verify successful completion

            sys.exit(0)

        except Exception as e:
            # In test mode, failures are expected
            if test:
                # Still output metrics in the requested format
                if format == 'prometheus':
                    click.echo(observer.format_prometheus_metrics())
                sys.exit(1)
            else:
                click.echo(f"ERROR: Workflow execution failed: {e}", err=True)
                sys.exit(1)

    except WorkflowParseError as e:
        click.echo(f"ERROR: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"ERROR: Unexpected error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
