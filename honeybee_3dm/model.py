"""Creating Honeybee model objects from rhino3dm surfaces and closed volumes"""
import os
import warnings

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
from .fromjson import read_json


# TODO: Add an argument to let the user choose the layers and assign energy and radiance
# properties if desired.
def import_3dm(path, name=None, *, config_path=None, visibility=True):
    """Import a rhino3dm file as a Honeybee model.

    This function outputs a Honeybee model from the faces, shades, apertures, and doors
    on a rhino3dm file. By default, all the rhino objects will be converted to Honeybee
    Faces based on the objects normal direction. A config file can be used to assign
    objects to specific Honeybee face types and Honeybee object types.

    Args:
        path: A text string for the path to the rhino3dm file.
        name: A text string that will be used as the name of the Honeybee
            model. Default will be the same as Rhino file name.
        config_path: A text string path to the config file on disk.
            Defaults to not using a config file.
        visibility: Bool. If set to False then the objects on an "off"
            layer in Rhino3dm will also be imported. Defaults to True.

    Returns:
        A Honeybee model.
    """
    # CONFIG FILE
    assert os.path.isfile(config_path), f'Config file not found.'
    # Get the config file as a directory
    config = read_json(config_path)

    # RHINO FILE
    if not os.path.isfile(path):
        warnings.warn(
            f'The path {path} is not a valid path. Please try using "r" prefix to'
            ' the file path.'
        )
        return []
    name = name or '.'.join(os.path.basename(path).split('.')[:-1])
    name = clean_string(name)
    rhino3dm_file = rhino3dm.File3dm.Read(path)
    if not rhino3dm_file:
        raise ValueError(f'Input Rhino file: {path} returns None object.')
    warnings.warn(
        f'*****The rhino file MUST be saved in the SHADED mode for'
        ' Honeybee to work.*****'
    )

    # TODO: RADIANCE.MAT FILE
    model_tolerance = rhino3dm_file.Settings.ModelAbsoluteTolerance
    model_angle_tolerance = rhino3dm_file.Settings.ModelAngleToleranceDegrees
    model_unit = get_unit_system(rhino3dm_file)

    # Honeybee Faces, Shades, Apertures and Doors
    hb_faces, hb_shades, hb_apertures, hb_doors = import_faces(
            rhino3dm_file, model_tolerance, visibility, config)

    # Honeybee Grid objects if they are tied to a Honeybee layer in config file
    if config['HB_layers']['HB_grid']:
        hb_grids = import_grids(rhino3dm_file, model_tolerance, 
            visibility=visibility, config=config)
    else:
        hb_grids = []

    # Honeybee Room objects if they are tied to a Honeybee layer in config file
    if config['HB_layers']['HB_room']:
        hb_rooms = import_rooms(rhino3dm_file, model_tolerance, visibility, config)
    else:
        hb_rooms = []

    # Honeybee Model
    hb_model = Model(
        name,
        hb_rooms,
        hb_faces,
        hb_shades,
        hb_apertures,
        hb_doors,
        units=model_unit,
        tolerance=model_tolerance,
        angle_tolerance=model_angle_tolerance
    )
    # Assigning grids to Honeybee model
    hb_model.properties.radiance.sensor_grids = hb_grids
    # Returning a Honeybee model
    return hb_model
