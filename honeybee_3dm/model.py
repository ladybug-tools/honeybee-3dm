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


# TODO: Add an argument to let the user choose the layers and assign energy and radiance
# properties if desired.
def import_3dm(path, name=None,*, visibility=True):
    """Import a rhino3dm file as a Honeybee model.

    This function outputs a Honeybee model from the faces, shades, apertures, and doors
    on a rhino3dm file. Currently, this method works with faces only. In future,
    this method will support translating close volumes in Honeybee models as well.

    Args:
        path: A text string for the path to the rhino3dm file.
        name: A text string that will be used as the name of the Honeybee
            model. Default will be the same as Rhino file name.
        visibility: Bool. If set to False then the objects on an "off"
            layer in Rhino3dm will also be imported. Defaults to True.

    Returns:
        A Honeybee model.
    """
    assert os.path.isfile(path), f'{path} is not a valid fileptah.'

    name = name or '.'.join(os.path.basename(path).split('.')[:-1])
    name = clean_string(name)

    rhino3dm_file = rhino3dm.File3dm.Read(path)

    if not rhino3dm_file:
        raise ValueError(f'Input Rhino file: {path} returns None object.')
    
    hb_layers = ['HB_wall', 'HB_roof', 'HB_floor', 'HB_aperture', 'HB_shade', 'HB_door',
        'HB_grid', 'HB_view']
    
    warnings.warn(
        f'*****The rhino file MUST be saved in the SHADED mode for Honeybee to work.*****'
    )
    warnings.warn(
        f'Honeybee layers are {hb_layers}.'
        ' To import objects on other layers, you can either rename' 
        ' them to one of the appropriate Honeybee layers or'
        ' make it a child of an appropriate Honeybee layer.'
    )
    model_tolerance = rhino3dm_file.Settings.ModelAbsoluteTolerance
    model_angle_tolerance = rhino3dm_file.Settings.ModelAngleToleranceDegrees
    model_unit = get_unit_system(rhino3dm_file)

    # Honeybee Rooms
    hb_rooms = import_rooms(rhino3dm_file, model_tolerance, visibility)
    # Honeybee Faces
    hb_faces = import_faces(rhino3dm_file, model_tolerance, visibility)[0]
    # Honeybee Shades
    hb_shades = import_faces(rhino3dm_file, model_tolerance, visibility)[1]
    # Honeybee Apertures
    hb_apertures = import_faces(rhino3dm_file, model_tolerance, visibility)[2]
    # Honeybee Doors
    hb_doors = import_faces(rhino3dm_file, model_tolerance, visibility)[3]
    # Honeybee Grids
    hb_grids = import_grids(rhino3dm_file, model_tolerance, visibility=visibility)
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
