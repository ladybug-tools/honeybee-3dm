"""Import Rhino surfaces as Honeybee grid objects from a Rhino3DM file."""
import warnings
# The Rhino3dm library provides the ability to access content of a Rhino3dm
# file from outside of Rhino
import rhino3dm

# Importing Honeybee dependencies
from honeybee_radiance.sensorgrid import SensorGrid
from honeybee.typing import clean_and_id_string, clean_string

# Importing dependencies from Honeybee-3dm package
from .togeometry import brep2d_to_face3d, mesh_to_mesh3d, check_planarity
from .helper import filter_objects_by_layer


# TODO: expose an option to change the target layer name
# TODO: Grid size and offset will have to provided using the config file


def import_grids(rhino3dm_file, tolerance, grid_size=1, grid_offset=0):
    """Creates Honeybee grids from a rhino3dm file.

    This function assumes all the grid objects are under a layer named ``grid``.

    Args:
        rhino3dm_file: The rhino file from which Honeybee grids will be created.
        tolerance: A rhino3dm tolerance object. Tolerance set in the rhino file.
        grid_size: Grid size. Defaults to 1.
        grid_offset: Grid offset from the grid geometry. Defaults to 0.

    Returns:
        A list of Honeybee grids.
    """

    # Objects from rhino file
    try:
        grid_objs = filter_objects_by_layer(rhino3dm_file, 'grid')
        warnings.warn(
            'Only objects on layer "grid" will be used to create grids.')
    except ValueError:
        # no layer named grid
        return []

    hb_grids = []

    for obj in grid_objs:
        geo = obj.Geometry

        # If it's a Brep
        if isinstance(geo, rhino3dm.Brep):
            
            # Check if the Brep is planar
            if check_planarity(geo):
                face3d = brep2d_to_face3d(geo, tolerance)[0]

                # Check if the Brep has curved edges
                try:
                    mesh3d = face3d.mesh_grid(grid_size, grid_size, grid_offset)
                except AssertionError:
                    warnings.warn(
                        'Breps with curved edges are not supported'
                        ' for grids as of now. Please Mesh them in Rhino and try again.'
                    )
                    continue
                # TODO: Find a way to Implement a method to create grids from a planar
                # TODO geometry with curved edges
            else:
                warnings.warn(
                    'A Non-planar Brep is not handled by Honeybee for grids.' 
                    ' It is ignored.'
                )
                continue

        # If it's a Mesh
        elif isinstance(geo, rhino3dm.Mesh):
            mesh3d = mesh_to_mesh3d(geo)

        name = obj.Attributes.Name
        obj_name = name or clean_and_id_string('grid')
        args = [clean_string(obj_name), mesh3d]
        hb_grids.append(SensorGrid.from_mesh3d(*args))

    return hb_grids
