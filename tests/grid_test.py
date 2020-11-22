import pytest
import rhino3dm
from honeybee_3dm.model import import_3dm
from honeybee_radiance.sensorgrid import SensorGrid
from ladybug_geometry.geometry3d import Point3D, Vector3D, Face3D


def test_grids():
    path = './tests/assets/test.3dm'
    rhino3dm_file = rhino3dm.File3dm.Read(path)
    tolerance = rhino3dm_file.Settings.ModelAbsoluteTolerance
    model = import_3dm(path)
    grid = model.properties.radiance.sensor_grids[0]
    assert isinstance(grid, SensorGrid)
    grid_names = [grid.display_name for grid in model.properties.radiance.sensor_grids]
    assert 'test-grid' in grid_names
    assert 'circular-grid' in grid_names
    assert grid.identifier == 'test-grid'
    assert grid.display_name == 'test-grid'
    assert len(grid.sensors) == 50
