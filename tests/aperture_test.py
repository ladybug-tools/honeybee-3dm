import rhino3dm
from math import isclose
from honeybee_3dm.model import import_3dm
from ladybug_geometry.geometry3d import Point3D, Vector3D, Face3D
from honeybee.boundarycondition import Outdoors


def test_apertures():
    path = './tests/assets/test.3dm'
    config_path = './tests/assets/config.json'
    rhino3dm_file = rhino3dm.File3dm.Read(path)
    tolerance = rhino3dm_file.Settings.ModelAbsoluteTolerance
    
    # Model with config file
    model = import_3dm(path, config_path=config_path)
    assert 'WindowEast' in [aperture.display_name for aperture in model.apertures]
    apertures = [
        aperture for aperture in model.apertures if
            aperture.display_name == 'WindowEast']
    aperture = apertures[0]
    assert aperture.vertices[0].is_equivalent(Point3D(5, 2.615265, 0.296184), tolerance)
    assert aperture.vertices[1].is_equivalent(Point3D(5, 7.105553, 0.296184), tolerance)
    assert aperture.vertices[2].is_equivalent(Point3D(5, 7.105553, 2.769152), tolerance)
    assert aperture.vertices[3].is_equivalent(Point3D(5, 2.615265, 2.769152), tolerance)
    assert aperture.upper_left_vertices[0].is_equivalent(Point3D
        (5, 2.615265, 2.769152), tolerance)
    assert aperture.center.is_equivalent(Point3D(5, 4.860409, 1.532668), tolerance)
    assert aperture.identifier == 'WindowEast'
    assert aperture.display_name == 'WindowEast'
    assert isinstance(aperture.geometry, Face3D)
    assert len(aperture.vertices) == 4
    assert len(aperture.triangulated_mesh3d.faces) == 2
    assert aperture.normal == Vector3D(1, 0, 0)
    assert isclose(aperture.area, 11.104336, abs_tol=tolerance)
    assert isclose(aperture.perimeter, 13.926511, abs_tol=tolerance)
    assert isinstance(aperture.boundary_condition, Outdoors)
    assert not aperture.is_operable
    assert not aperture.has_parent
    
    # Model without config file
    model = import_3dm(path)
    assert not model.apertures
