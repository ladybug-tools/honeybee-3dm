"""Creating Honeybee grid objects from rhino3dm surfces"""

import rhino3dm
from honeybee.model import Model
from honeybee_radiance.sensorgrid import SensorGrid
from honeybee_radiance.writer import model_to_rad_folder

from .room import to_room
from .face import to_face
from .tojson import to_json
from .togeometry import brep2d_to_face3d


def to_grid(path):
    """Creates Honeybee grids from a rhino3dm file

    Args:
        path (A string): The path to the rhino3dm file
    Returns:
        hb_grids (A list): A list of Honeybee grids
    """
    rhino3dm_file = rhino3dm.File3dm.Read(path)
    tolerance = rhino3dm_file.Settings.ModelAbsoluteTolerance

    layer_dict = {
        layer.Name: layer.Index for layer in rhino3dm_file.Layers}

    # Grids from rhino file
    grid_objs = [object.Geometry for object in rhino3dm_file.Objects
                 if object.Attributes.LayerIndex == layer_dict['grid']]

    # Face3D objects for the grids
    grid_face3ds = [brep2d_to_face3d(obj, tolerance)[0] for obj in grid_objs]

    grids = []
    # Creating Ladybug Grid objects
    for face in grid_face3ds:
        try:
            grids.append(face.mesh_grid(1, 1, 0))
        except AssertionError:
            pass

    # Creating Honeybee Grid objects
    hb_grids = [SensorGrid.from_mesh3d(str(i), grids[i])
                for i in range(len(grids))]

    return hb_grids
