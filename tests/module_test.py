import pytest

from honeybee_3dm.room import to_room
from honeybee_3dm.face import to_face
from honeybee_3dm.togeometry import mesh_to_face3d


def test_import():
    assert to_room
    assert to_face
    assert mesh_to_face3d
