from honeybee.model import Model
from honeybee.shade import Shade
from honeybee.door import Door
from honeybee.aperture import Aperture
from honeybee.facetype import face_types
from honeybee_3dm.model import import_3dm


def test_model():
    path = './tests/assets/test.3dm'
    config_path = './tests/assets/config.json'
    model = import_3dm(path, config_path=config_path)
    assert isinstance(model, Model)
    assert model.display_name == 'test'
    assert model.angle_tolerance == 1.0
    assert model.tolerance == 0.01
    assert model.units == "Meters"
    assert len(model.apertures) == 1
    assert isinstance(model.apertures[0], Aperture)
    assert len(model.doors) == 1
    assert isinstance(model.doors[0], Door)
    assert len(model.shades) == 1
    assert isinstance(model.shades[0], Shade)
    assert len(model.faces) == 6
    walls = [face for face in model.faces if face.type == face_types.wall]
    roofs = [face for face in model.faces if face.type == face_types.roof_ceiling]
    floors = [face for face in model.faces if face.type == face_types.floor]
    airwalls = [face for face in model.faces if face.type == face_types.air_boundary]
    assert len(walls) == 4
    assert len(roofs) == 1
    assert len(floors) == 1
    assert len(airwalls) == 0
    assert model.properties.radiance.sensor_grids
