import pytest
from honeybee.face import Face
from honeybee_3dm.face import to_face


def test_face():
    relative_path = './tests/assets/test.3dm'
    room = to_face(relative_path)[0]
    assert isinstance(room, Face)
