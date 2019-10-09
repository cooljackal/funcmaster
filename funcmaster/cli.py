import click
import importlib
from funcmaster import execute_process


@click.command()
@click.option(
    "--module",
    "-m",
    required=True,
    type=str,
    help="name of module that contains process definition",
)
@click.option(
    "--process",
    "-p",
    required=True,
    type=str,
    help="name of process function in module",
)
def main(module, process):
    """Simple interface to execute funcmaster processes."""
    try:
        imported_module = importlib.import_module(module)
        target_process = getattr(imported_module, process)
    except ModuleNotFoundError:
        click.echo("Module %s was not found!" % module)
    except AttributeError:
        click.echo("Process %s was not found in module %s" % (process, module))
    else:
        execute_process(target_process)
