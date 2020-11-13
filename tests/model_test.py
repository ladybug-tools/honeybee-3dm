from honeybee.model import Model
from honeybee_3dm.model import import_3dm


def test_model():
    path = './tests/assets/test.3dm'
    model = import_3dm(path)
    assert isinstance(model, Model)
    assert model.display_name == 'test'
    assert model.angle_tolerance == 1.0
    assert model.tolerance == 0.01
    assert model.units == "Meters"
    assert len(model.apertures) == 1
    assert len(model.doors) == 1
    assert len(model.shades) == 1
    assert len(model.faces) == 6


def test_assign_name():
    path = './tests/assets/test.3dm'
    model = import_3dm(path, name='new_model')
    assert model.identifier == 'new_model'
    assert model.display_name == 'new_model'
