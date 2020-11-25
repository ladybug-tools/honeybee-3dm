"""Import Rhino surfaces as Honeybee grid objects from a Rhino3DM file."""
import warnings
# The Rhino3dm library provides the ability to access content of a Rhino3dm
# file from outside of Rhino
import rhino3dm

# Importing Honeybee dependencies
from honeybee_radiance.sensorgrid import SensorGrid
from honeybee.typing import clean_and_id_string, clean_string

# Importing dependencies from Honeybee-3dm package
from .togeometry import brep_to_face3d, mesh_to_mesh3d, check_planarity
from .helper import filter_objects_by_layer, HB_layers


# TODO: expose an option to change the target layer name
# TODO: Grid size and offset will have to provided using the config file


def import_grids(rhino3dm_file, tolerance, grid_size=1, grid_offset=0, *,
    visibility=True, config=None):
    """Creates Honeybee grids from a rhino3dm file.

    This function assumes all the grid objects are under a layer named ``grid``.

    Args:
        rhino3dm_file: The rhino file from which Honeybee grids will be created.
        tolerance: A rhino3dm tolerance object. Tolerance set in the rhino file.
        grid_size: Grid size. Defaults to 1.
        grid_offset: Grid offset from the grid geometry. Defaults to 0.
        visibility: Bool. If set to False then the objects on an "off"
            layer in Rhino3dm will also be imported. Defaults to True.
        config: A dictionary. The config file as a dictionary object.
            Defaults to None.
    Returns:
        A list of Honeybee grids.
    """
    hb_grids = []
    config = config
    # If config file is provided and any Rhino layer is tied to HB_grid layer
    if config and config['HB_layers']['HB_grid']:
        grid_objs = filter_objects_by_layer(rhino3dm_file, 
            config['HB_layers']['HB_grid'], visibility=visibility)
        
        for obj in grid_objs:
            geo = obj.Geometry
            # If it's a Brep
            if isinstance(geo, rhino3dm.Brep):
                # Check if the Brep is planar
                if check_planarity(geo):
                    mesh3d = brep_to_face3d(geo, tolerance).mesh_grid(grid_size,
                        grid_size, grid_offset)
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
