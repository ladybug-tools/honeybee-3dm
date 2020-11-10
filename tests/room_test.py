import pytest
from honeybee.room import Room
from honeybee_3dm.room import to_room


def test_room():
    relative_path = './tests/assets/test.3dm'
    room = to_room(relative_path)[0]
    assert isinstance(room, Room)
