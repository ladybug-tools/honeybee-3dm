"""honeybee-3dm command line interface."""

import sys
import pathlib
import os

import click
from click.exceptions import ClickException

from .model import import_3dm


@click.group()
def main():
    """honeybee-3dm commands entry points."""
    pass


@main.command('translate')
@click.argument('rhino-file')
@click.option(
    '--name', '-n', help='Name of the output HBJSON file. If not provided, "unnamed"'
    ' will be used.', default='unnamed'
)
@click.option(
    '--folder', '-f', help='Path to folder where HBJSON will be written.',
    type=click.Path(exists=False, file_okay=False, resolve_path=True, dir_okay='True'),
    default='.', show_default=True
)
@click.option(
    '--config', '-cf', help='File Path to the config.json file.',
    type=click.Path(exists=True),
    default=None, show_default=True
)
def translate_recipe(rhino_file, name, folder, config):
    """Translate a rhino file to HBJSON.
    
    \b
    Args:
        rhino-file: Path to the rhino file.
    """
    folder = pathlib.Path(folder)
    folder.mkdir(exist_ok=True)
    model = import_3dm(rhino_file, config_path=config)
    model.to_hbjson(name=name, folder=folder)
    hbjson_file = os.path.join(folder, name + '.hbjson')

    try:
        output_file = hbjson_file
    except Exception as e:
        raise ClickException(f'HBJSON generation failed:\n{e}')
    else:
        print(f'Success: {output_file}', file=sys.stderr)
        return sys.exit(0)
