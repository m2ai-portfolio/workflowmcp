"""CLI commands for Copilot SDK."""

import json
import sys
import click

from workflow_mcp.sdk import load_skill, run_skill, list_skills


@click.group()
def cli():
    """Copilot SDK: Extensible Agent Skills."""
    pass


@cli.command()
@click.option('--name', required=True, help='Name of the skill to load')
@click.option('--config', default='{}', help='JSON configuration for the skill')
def load_skill_cmd(name, config):
    """Load a skill and return handle information."""
    try:
        # Parse config JSON
        try:
            config_dict = json.loads(config)
        except json.JSONDecodeError as e:
            click.echo(f"ERROR: Invalid JSON in config: {e}", err=True)
            sys.exit(1)

        # Load the skill
        handle = load_skill(name, config_dict)

        # Return handle information as JSON
        output = {
            'handle': handle.name,
            'name': handle.name,
            'config': handle.config,
            'status': 'loaded'
        }

        click.echo(json.dumps(output, indent=2))
        sys.exit(0)

    except ValueError as e:
        click.echo(f"ERROR: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"ERROR: Unexpected error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--handle', required=True, help='Handle name (skill name) to execute')
@click.option('--input', 'input_json', required=True, help='JSON input data for the skill')
def run_skill_cmd(handle, input_json):
    """Execute a skill with input data."""
    try:
        # Parse input JSON
        try:
            input_data = json.loads(input_json)
        except json.JSONDecodeError as e:
            click.echo(f"ERROR: Invalid JSON in input: {e}", err=True)
            sys.exit(1)

        # Load the skill (will use cached version if already loaded)
        skill_handle = load_skill(handle)

        # Run the skill
        result = run_skill(skill_handle, input_data)

        # Output result as JSON
        click.echo(json.dumps(result, indent=2))
        sys.exit(0)

    except ValueError as e:
        click.echo(f"ERROR: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"ERROR: Unexpected error: {e}", err=True)
        sys.exit(1)


@cli.command()
def list_skills_cmd():
    """List all available skills."""
    try:
        skills = list_skills()

        # Print one skill per line
        for skill in skills:
            click.echo(skill)

        sys.exit(0)

    except Exception as e:
        click.echo(f"ERROR: Unexpected error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
