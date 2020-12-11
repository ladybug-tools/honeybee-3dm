"""Create Honeybee grid objects from objects in a rhino file."""

import warnings
import rhino3dm

from honeybee_radiance.sensorgrid import SensorGrid
from honeybee.typing import clean_and_id_string, clean_string

from .togeometry import brep_to_face3d, mesh_to_mesh3d, check_planarity, solid_to_face3d, to_face3d
from .layer import objects_on_layer, objects_on_parent_child


def import_grids(rhino3dm_file, layer, *, grid_controls=None, child_layer=False,
    tolerance=None):
    """Creates Honeybee grids from a rhino3dm file.

    This function assumes all the grid objects are under a layer named ``grid``.

    Args:
        rhino3dm_file: The rhino file from which Honeybee grids will be created.
        layer: A Rhino3dm layer object.
        grid_controls: A tuple of values for grid_size and grid_offset.
            Defaults to None. This will employ the grid setting of (1.0, 1.0, 0.0)
            for grid-size-x, grid-size-y, and grid-offset respectively.
        child_layer: A bool. True will generate grids from the objects on the child layer
            of a layer in addition to the objects on the parent layer. Defaults to False.
        tolerance: A rhino3dm tolerance object. Tolerance set in the rhino file.
            .
    Returns:
        A list of Honeybee grids.
    """
    hb_grids = []
    # if objects on child layers are not requested
    if not child_layer:
        grid_objs = objects_on_layer(rhino3dm_file, layer)
    
    # if objects on child layers are requested
    if child_layer:
        grid_objs = objects_on_parent_child(rhino3dm_file, layer.Name)
    
    # Set default grid settings if not provided
    if not grid_controls:
        grid_controls = (1.0, 1.0, 0.0)

    for obj in grid_objs:
        geo = obj.Geometry
        
        # If it's a Mesh use it to create grids
        # This is done so that if a user has created mesh with certain density
        # the same can be used to create grids
        if isinstance(geo, rhino3dm.Mesh):
            mesh3d = mesh_to_mesh3d(geo)
            name = obj.Attributes.Name
            obj_name = name or clean_and_id_string('Grid')
            args = [clean_string(obj_name), mesh3d]
            hb_grids.append(SensorGrid.from_mesh3d(*args))

        else:
            for face in to_face3d(obj, tolerance):
                if face.normal.z == -1:
                    continue
                else:
                    try:
                        mesh3d = face.mesh_grid(grid_controls[0],
                            grid_controls[0], grid_controls[1])
                    except AssertionError:
                        raise AssertionError(
                        f'Object with ID: {obj.Attributes.Id} is not supported for grids'
                    )
                    name = obj.Attributes.Name
                    obj_name = name or clean_and_id_string('Grid')
                    args = [clean_string(obj_name), mesh3d]
                    hb_grids.append(SensorGrid.from_mesh3d(*args))

    return hb_grids
