import pytest
import rhino3dm
from pathlib import Path
from honeybee.room import Room
from honeybee_3dm.room import to_room


def test_room():
    path = str((Path.cwd()).joinpath('tests', 'test.3dm'))
    room = to_room(path)[0]
    assert isinstance(room, Room)
