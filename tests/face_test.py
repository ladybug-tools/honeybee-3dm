import pytest
import rhino3dm
from pathlib import Path
from honeybee.face import Face
from honeybee_3dm.face import to_face


def test_room():
    path = str((Path.cwd()).joinpath('tests', 'test.3dm'))
    room = to_face(path)[0]
    assert isinstance(room, Face)
