"""Import Rhino surfaces as Honeybee grid objects from a Rhino3DM file."""

from honeybee_radiance.sensorgrid import SensorGrid

from .togeometry import brep2d_to_face3d
from .helper import filter_objects_by_layer


# TODO: expose grid size inputs
# TODO: expose an option to change the target layer name
def import_grids(rhino3dm_file, tolerance):
    """Creates Honeybee grids from a rhino3dm file.

    This function assumes all the grid objects are under a layer named ``grid``.

    Args:
        rhino3dm_file: The rhino file from which Honeybee faces will be created.
        tolerance: A rhino3dm tolerance object. Tolerance set in the rhino file.

    Returns:
        A list of Honeybee grids.
    """

    # Grids from rhino file
    try:
        grid_objs = filter_objects_by_layer(rhino3dm_file, 'grid')
    except ValueError:
        # no layer named grid
        return []

    # TODO: Handle other objects like Mesh and Brep
    # Face3D objects for the grids
    grid_face3ds = [brep2d_to_face3d(obj.Geometry, tolerance)[0] for obj in grid_objs]

    grids = []
    # Creating Ladybug Grid objects
    for face in grid_face3ds:
        try:
            # TODO: Expose the input values for meshing the input geometries
            grids.append(face.mesh_grid(1, 1, 0))
        except AssertionError:
            # TODO(Devang): Clarify why the Assertion error is happening
            pass

    # Creating Honeybee Grid objects
    # TODO(Devang): User object name for grid if provided in Rhino model
    hb_grids = [SensorGrid.from_mesh3d(str(c), grid) for c, grid in enumerate(grids)]

    return hb_grids
