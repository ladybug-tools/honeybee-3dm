import pytest
from honeybee_3dm.model import import_3dm
from ladybug_geometry.geometry3d import Point3D, Vector3D


def test_grids():
    path = './tests/assets/test.3dm'
    model = import_3dm(path)
    # Check for User provided name
    assert 'test-grid' in [grid.display_name for grid in model.properties.radiance.sensor_grids]
