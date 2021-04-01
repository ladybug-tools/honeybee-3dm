import os
from click.testing import CliRunner
from honeybee_3dm.cli import translate_recipe
from ladybug.futil import nukedir


def test_write_hbjson():
    """Check whether an HBJSON can be written."""
    runner = CliRunner()
    file_path = './tests/assets/test.3dm'
    config_path = './tests/assets/config.json'
    target_path = './tests/target'

    result = runner.invoke(translate_recipe, [
        file_path, '--name', 'test', '--folder', target_path, '--config', config_path
        ])

    assert result.exit_code == 0
    hbjson_path = os.path.join(target_path, 'test.hbjson')
    assert os.path.isfile(hbjson_path)
    nukedir(target_path, True)
