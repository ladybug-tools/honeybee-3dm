import pytest
from honeybee_3dm.model import import_3dm
from ladybug_geometry.geometry3d import Point3D, Vector3D

path = './tests/assets/test.3dm'
model = import_3dm(path)


def test_apertures():
    # Check for User provided name
    assert 'Window_East' in [aperture.display_name for aperture in model.apertures]
    # Check for vertices & normal
    aperture = [
        aperture for aperture in model.apertures if aperture.display_name == 'Window_East']
    assert aperture[0].vertices[0].is_equivalent(Point3D(5, 2.615265, 0.296184), 0.01)
    assert aperture[0].vertices[1].is_equivalent(Point3D(5, 7.105553, 0.296184), 0.01)
    assert aperture[0].vertices[2].is_equivalent(Point3D(5, 7.105553, 2.769152), 0.01)
    assert aperture[0].vertices[3].is_equivalent(Point3D(5, 2.615265, 2.769152), 0.01)
    assert aperture[0].normal == Vector3D(1, 0, 0)
