"""Creating Honeybee model objects from rhino3dm surfaces and closed volumes"""
import os
import rhino3dm

from honeybee.model import Model

from .face import import_objects, import_objects_with_config
from .helper import get_unit_system, check_parent_in_config
from .layer import child_parent_dict, visible_layers
from .config import check_config


def import_3dm(path, name=None, *, config_path=None):
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

    Returns:
        A Honeybee model.
    """
    # RHINO FILE
    if not os.path.isfile(path):
        raise FileNotFoundError(
            'The path to rhino file is not valid.'
            )
    rhino3dm_file = rhino3dm.File3dm.Read(path)
    if not rhino3dm_file:
        raise ValueError(f'Input Rhino file: {path} returns None object.')

    # CONFIG FILE
    if config_path:
        if not os.path.isfile(config_path):
            raise FileNotFoundError(
                'The path is not a valid path.'
                ' If file exists, try using double backslashes in file path'
                ' and try again.'
            )
        # Validate the config file and get it as a directory

        config = check_config(rhino3dm_file, config_path)
    else:
        config = None

    # Extracting unit parameters from rhino
    model_tolerance = rhino3dm_file.Settings.ModelAbsoluteTolerance
    model_angle_tolerance = rhino3dm_file.Settings.ModelAngleToleranceDegrees
    model_unit = get_unit_system(rhino3dm_file)

    # Place holders
    hb_rooms, hb_faces, hb_shades, hb_apertures, hb_doors, hb_grids = tuple(
            [[] for _ in range(6)])

    # A dictionary with child layer : parent layer structure
    child_to_parent = child_parent_dict(rhino3dm_file)

    # Get all the visible layers from rhino
    if visible_layers(rhino3dm_file):
        rhino_visible_layers = visible_layers(rhino3dm_file)
        rhino_visible_layer_names = [layer.Name for layer in rhino_visible_layers]
    else:
        raise ValueError(
            'Please turn on the layers in rhino you wish to import objects from.'
        )

    # If config is provided
    if config:
        
        for layer in rhino3dm_file.Layers:

            # If the layer is not in config and not "on" in rhino, ignore
            if layer.Name not in config['layers'] and \
                layer.Name not in rhino_visible_layer_names:
                continue

            # Import objects from each layer in the config file
            elif layer.Name in config['layers']:
                hb_objs = import_objects_with_config(
                    rhino3dm_file, layer, model_tolerance, config=config)
                hb_faces.extend(hb_objs[0])
                hb_shades.extend(hb_objs[1])
                hb_apertures.extend(hb_objs[2])
                hb_doors.extend(hb_objs[3])
                hb_grids.extend(hb_objs[4])

            # skip child layers that might already have been imported
            elif check_parent_in_config(rhino3dm_file, config,
                layer.Name, child_to_parent[layer.Name]):
                continue

            # Import objects from each layer not in the config file
            elif layer.Name in rhino_visible_layer_names:
                hb_faces.extend(import_objects(rhino3dm_file, layer,
                    tolerance=model_tolerance))
    
    else:  # If config is not provided
        # Only use layers that are "on" in rhino
        for layer in rhino_visible_layers:
            hb_faces.extend(import_objects(rhino3dm_file, layer,
                tolerance=model_tolerance))
    
    # Honeybee model name
    name = name or '.'.join(os.path.basename(path).split('.')[:-1])

    # Honeybee Model
    hb_model = Model(
        identifier=name,
        rooms=hb_rooms,
        orphaned_faces=hb_faces,
        orphaned_shades=hb_shades,
        orphaned_apertures=hb_apertures,
        orphaned_doors=hb_doors,
        units=model_unit,
        tolerance=model_tolerance,
        angle_tolerance=model_angle_tolerance
    )
    # Assigning grids to Honeybee model
    hb_model.properties.radiance.sensor_grids = hb_grids
    # Returning a Honeybee model
    return hb_model
