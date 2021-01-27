from honeybee_3dm.model import import_3dm
from ladybug_geometry.geometry3d import Point3D, Vector3D


def test_walls():
    path = './tests/assets/test.3dm'
    config_path = './tests/assets/config.json'
    model = import_3dm(path, config_path=config_path)
    # Check for User provided name
    assert 'southwall' in [face.display_name for face in model.faces]
    # Check for vertices & normal
    south_wall = [face for face in model.faces if face.display_name == 'southwall']
    assert south_wall[0].vertices[0].is_equivalent(Point3D(0, 0, 0), 0.01)
    assert south_wall[0].vertices[1].is_equivalent(Point3D(5, 0, 0), 0.01)
    assert south_wall[0].vertices[2].is_equivalent(Point3D(5, 0, 3), 0.01)
    assert south_wall[0].vertices[3].is_equivalent(Point3D(0, 0, 3), 0.01)
    assert south_wall[0].normal == Vector3D(0, -1, 0)
