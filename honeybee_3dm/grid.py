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
from .helper import objects_on_parent_child, HB_layers, check_grid_controls


# TODO: expose an option to change the target layer name
# TODO: Grid size and offset will have to provided using the config file


def import_grids(rhino3dm_file, tolerance, *, visibility=True, config=None):
    """Creates Honeybee grids from a rhino3dm file.

    This function assumes all the grid objects are under a layer named ``grid``.

    Args:
        rhino3dm_file: The rhino file from which Honeybee grids will be created.
        tolerance: A rhino3dm tolerance object. Tolerance set in the rhino file.
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
        
        # Grid controls
        if config['grid_controls']:
            # grid_size_x, grid_size_y, grid_offset = tuple([config['grid_controls'][k]
            #     for k in config['grid_controls']])
            grid_settings = [config['grid_controls'][k]
                for k in config['grid_controls']]
            if check_grid_controls(grid_settings):
                grid_controls = grid_settings
            else:
                warnings.warn(
                    'Grid setting from config file not applied.'
                    ' Please make sure grid controls are floating point numbers'
                    ' and try again.'
                )
                grid_controls = [1.0, 1.0, 0.0]

        grid_objs = objects_on_parent_child(rhino3dm_file, 
            config['HB_layers']['HB_grid'], visibility=visibility)
        
        for obj in grid_objs:
            geo = obj.Geometry
            # If it's a Brep
            if isinstance(geo, rhino3dm.Brep):
                # Check if the Brep is planar
                if check_planarity(geo):
                    try:
                        mesh3d = brep_to_face3d(geo, tolerance).mesh_grid(grid_controls[0],
                            grid_controls[1], grid_controls[2])
                    except AttributeError:
                        warnings.warn(
                            'Please turn on the shaded mode in rhino, save the file,'
                        ' and try again.'
                        )
                        continue
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
            obj_name = name or clean_and_id_string('Grid')
            args = [clean_string(obj_name), mesh3d]
            hb_grids.append(SensorGrid.from_mesh3d(*args))

    return hb_grids
