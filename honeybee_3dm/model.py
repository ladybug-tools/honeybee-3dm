"""Creating Honeybee model objects from rhino3dm surfaces and closed volumes"""
import os

# The Rhino3dm library provides the ability to access content of a Rhino3dm
# file from outside of Rhino
import rhino3dm

# Importing core Honeybee dependency
from honeybee.model import Model
from honeybee.typing import clean_string

# Importing dependencies from Honeybee-3dm package
from .room import import_rooms
from .face import import_faces
from .grid import import_grids
from .helper import get_unit_system


# TODO: Add an argument to let the user choose the layers and assign energy and radiance
# properties if desired.
def import_3dm(path, name=None):
    """Import a rhino3dm file as a Honeybee model.

    This function outputs a Honeybee model from the faces, shades, apertures, and doors
    on a rhino3dm file. Currently, this method works with faces only. In future,
    this method will support translating close volumes in Honeybee models as well.

    Args:
        path: A text string for the path to the rhino3dm file.
        name: A text string that will be used as the name of the Honeybee
            model. Default will be the same as Rhino file name.

    Returns:
        A Honeybee model.
    """
    assert os.path.isfile(path), f'{path} is not a valid fileptah.'

    name = name or '.'.join(os.path.basename(path).split('.')[:-1])
    name = clean_string(name)

    rhino3dm_file = rhino3dm.File3dm.Read(path)

    if not rhino3dm_file:
        raise ValueError(f'Input Rhino file: {path} returns None object.')

    model_tolerance = rhino3dm_file.Settings.ModelAbsoluteTolerance
    model_angle_tolerance = rhino3dm_file.Settings.ModelAngleToleranceDegrees
    model_unit = get_unit_system(rhino3dm_file)

    # Honeybee faces
    hb_faces = import_faces(rhino3dm_file, model_tolerance)
    # Honeybee_rooms
    hb_rooms = import_rooms(rhino3dm_file, model_tolerance)
    # Honeybee grids
    hb_grids = import_grids(rhino3dm_file, model_tolerance)
    # Honeybee model
    hb_model = Model.from_objects(
        name,
        hb_faces + hb_rooms,
        units=model_unit,
        tolerance=model_tolerance,
        angle_tolerance=model_angle_tolerance
    )
    # Assigning grids to Honeybee model
    hb_model.properties.radiance.sensor_grids = hb_grids
    # Returning a Honeybee model
    return hb_model
