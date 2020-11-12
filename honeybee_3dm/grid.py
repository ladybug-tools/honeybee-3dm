"""Creating Honeybee grid objects from rhino3dm surfces"""

import rhino3dm
from honeybee.model import Model
from honeybee_radiance.sensorgrid import SensorGrid
from honeybee_radiance.writer import model_to_rad_folder

from .room import to_room
from .face import to_face
from .togeometry import brep2d_to_face3d


def to_grid(rhino3dm_file, tolerance):
    """Creates Honeybee grids from a rhino3dm file.

    Args:
        rhino3dm_file: The rhino file from which Honeybee faces will be created.
        tolerance: A rhino3dm tolerance object. Tolerance set in the rhino file.

    Returns:
        A list of Honeybee grids.
    """
    layer_dict = {
        layer.Name: layer.Index for layer in rhino3dm_file.Layers}

    try:
        # Grids from rhino file
        grid_objs = [object.Geometry for object in rhino3dm_file.Objects
                     if object.Attributes.LayerIndex == layer_dict['grid']]

        # Face3D objects for the grids
        grid_face3ds = [brep2d_to_face3d(obj, tolerance)[0]
                        for obj in grid_objs]

        grids = []
        # Creating Ladybug Grid objects
        for face in grid_face3ds:
            try:
                grids.append(face.mesh_grid(1, 1, 0))
            except AssertionError:
                pass

        # Creating Honeybee Grid objects
        hb_grids = [SensorGrid.from_mesh3d(str(c), grid)
                    for c, grid in enumerate(grids)]

        return hb_grids
    except KeyError:
        return None
