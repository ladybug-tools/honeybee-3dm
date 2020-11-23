import pytest
from honeybee_radiance.sensorgrid import SensorGrid
from honeybee_3dm.model import import_3dm


def test_grids():
    path = './tests/assets/test.3dm'
    model = import_3dm(path)
    grid_names = [grid.display_name for grid in model.properties.radiance.sensor_grids]
    assert 'test-grid' in grid_names
    assert 'circular-grid' in grid_names
    test_grid = [grid for grid in model.properties.radiance.sensor_grids if
        grid.display_name == 'test-grid'][0]
    assert isinstance(test_grid, SensorGrid)
    assert test_grid.identifier == 'test-grid'
    assert test_grid.display_name == 'test-grid'
    assert len(test_grid.sensors) == 50
