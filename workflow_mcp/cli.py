"""Command-line interface for WorkflowMCP."""

import json
import sys
from pathlib import Path
import click

from .core import parse_workflow, validate_workflow, visualize_workflow
from .monitoring import WorkflowObserver
from .sdk import get_registry


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


@cli.command()
@click.option('--workflow', required=True, help='Workflow name or YAML file path')
@click.option('--format', 'output_format', type=click.Choice(['json', 'prometheus']), default='json', help='Output format')
@click.option('--test', 'test_mode', is_flag=True, help='Run in test mode (simulate failure)')
def monitor(workflow: str, output_format: str, test_mode: bool):
    """Monitor workflow execution with real-time metrics."""
    try:
        # Try to resolve workflow path - first check if it's a file path
        workflow_path = Path(workflow)
        if not workflow_path.exists():
            # Try with .yaml extension
            workflow_path = Path(f"{workflow}.yaml")
            if not workflow_path.exists():
                click.echo(f"Error: Workflow file not found: {workflow}", err=True)
                sys.exit(1)

        # Create observer
        observer = WorkflowObserver(workflow_name=workflow_path.stem)

        # Simulate workflow run
        events = observer.simulate_run(str(workflow_path), inject_failure=test_mode)

        # Output in requested format
        if output_format == 'json':
            # Stream JSON lines to stdout (one per event)
            for event in events:
                click.echo(json.dumps(event))
        elif output_format == 'prometheus':
            # Output Prometheus metrics
            metrics = observer.get_metrics_prometheus()
            click.echo(metrics)

        # If in test mode, verify alert was emitted
        if test_mode:
            alerts = [e for e in events if e.get('type') == 'alert']
            if alerts:
                click.echo("\n[TEST MODE] Alert verification: PASS", err=True)
                click.echo(f"[TEST MODE] Emitted {len(alerts)} alert(s)", err=True)
            else:
                click.echo("\n[TEST MODE] Alert verification: FAIL - No alerts emitted", err=True)
                sys.exit(1)

        sys.exit(0)

    except Exception as e:
        click.echo(f"Error monitoring workflow: {e}", err=True)
        sys.exit(1)


# =============================================================================
# SDK CLI - Copilot SDK commands
# =============================================================================

@click.group()
@click.version_option(version="0.1.0")
def sdk_cli():
    """Copilot SDK - manage and invoke agent skills."""
    pass


@sdk_cli.command('load_skill')
@click.option('--name', required=True, help='Skill name to load')
def sdk_load_skill(name):
    """Load a skill module by name."""
    try:
        registry = get_registry()
        handle = registry.load_skill(name)

        # Output handle information
        click.echo(f"Loaded skill '{name}'")
        click.echo(f"Handle ID: {handle.handle_id}")
        click.echo(f"Module: {handle.module.__name__}")

        # Check for skill metadata
        if hasattr(handle.module, 'SKILL_DESCRIPTION'):
            click.echo(f"Description: {handle.module.SKILL_DESCRIPTION}")

        sys.exit(0)
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error loading skill: {e}", err=True)
        sys.exit(1)


@sdk_cli.command('run_skill')
@click.option('--handle', required=True, help='Skill handle ID or skill name')
@click.option('--input', 'input_data', required=True, help='JSON input data')
def sdk_run_skill(handle, input_data):
    """Run a skill with input data.

    The handle can be either:
    - A skill name (e.g., 'summarizer') - will be loaded automatically
    - A handle ID from a previous load_skill command
    """
    try:
        # Check input size limit
        if len(input_data) > 1_000_000:
            click.echo("Error: Input JSON too large", err=True)
            sys.exit(1)

        # Parse JSON input
        try:
            input_dict = json.loads(input_data)
        except json.JSONDecodeError as e:
            click.echo(f"Error: Invalid JSON input: {e}", err=True)
            sys.exit(1)

        # Run the skill
        registry = get_registry()

        # Try to run by handle ID first
        skill_handle = registry.get_handle(handle)

        if skill_handle is None:
            # Handle might be a skill name - try loading it
            try:
                skill_handle = registry.load_skill(handle)
            except (FileNotFoundError, ImportError) as e:
                click.echo(f"Error: No skill found with handle ID or name '{handle}'", err=True)
                click.echo(f"Details: {e}", err=True)
                sys.exit(1)

        # Run the skill using the handle
        result = skill_handle.invoke(input_dict)

        # Output result as JSON
        click.echo(json.dumps(result, indent=2))
        sys.exit(0)

    except KeyError as e:
        click.echo(f"Error: {e}", err=True)
        click.echo("Hint: Load the skill first with 'copilot_sdk load_skill --name <skill_name>'", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error running skill: {e}", err=True)
        sys.exit(1)


@sdk_cli.command('list_skills')
def sdk_list_skills():
    """List all available skills."""
    try:
        registry = get_registry()
        skills = registry.list_skills()

        if not skills:
            click.echo("No skills available")
            sys.exit(0)

        click.echo("Available skills:")
        for skill in skills:
            click.echo(f"  - {skill}")

        sys.exit(0)
    except Exception as e:
        click.echo(f"Error listing skills: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
