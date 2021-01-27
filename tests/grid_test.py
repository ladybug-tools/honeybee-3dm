from honeybee_radiance.sensorgrid import SensorGrid
from honeybee_3dm.model import import_3dm


def test_grids():
    path = './tests/assets/test.3dm'
    config_path = './tests/assets/config.json'

    
    # Model with config file
    model = import_3dm(path, config_path=config_path)
    grid_names = [grid.display_name for grid in model.properties.radiance.sensor_grids]
    
    assert 'test-grid' in grid_names
    test_grid = [grid for grid in model.properties.radiance.sensor_grids if
        grid.display_name == 'test-grid'][0]
    assert isinstance(test_grid, SensorGrid)
    assert test_grid.identifier == 'test-grid'
    assert test_grid.display_name == 'test-grid'
    assert len(test_grid.sensors) == 128
    print(test_grid.sensors[0])

    assert 'circular-grid' in grid_names
    circular_grid = [grid for grid in model.properties.radiance.sensor_grids if
        grid.display_name == 'circular-grid'][0]
    assert isinstance(circular_grid, SensorGrid)
    assert circular_grid.identifier == 'circular-grid'
    assert circular_grid.display_name == 'circular-grid'
    assert len(circular_grid.sensors) == 145
    
    # Model without a config file
    model = import_3dm(path)
    assert not model.properties.radiance.sensor_grids
