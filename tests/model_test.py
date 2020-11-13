import pytest
from honeybee.model import Model
from honeybee_3dm.model import to_model


path = './tests/assets/test.3dm'
model = to_model(path)


def test_model():
    assert isinstance(model, Model)
    assert model.display_name == 'unnamed'
    assert model.angle_tolerance == 1.0
    assert model.tolerance == 0.01
    assert model.units == "Meters"
    assert len(model.apertures) == 1
    assert len(model.doors) == 1
    assert len(model.shades) == 1
    assert len(model.faces) == 6
