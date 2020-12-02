"""Creating Honeybee model objects from rhino3dm surfaces and closed volumes"""
import os
import rhino3dm

from honeybee.model import Model
from honeybee.typing import clean_string

from .face import import_objects, import_objects_with_config
from .helper import get_unit_system
from .config import read_json, check_config, check_parent_in_config
from .layer import child_parent_dict


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
        # Get the config file as a directory
        config = read_json(config_path)
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

    # If config is provided
    if config and check_config(rhino3dm_file, config):
        
        for layer in rhino3dm_file.Layers:
            
            # Import objects from each layer in the config file
            if layer.Name in config['layers']:
                hb_objs = import_objects_with_config(
                    rhino3dm_file, layer, tolerance=model_tolerance,
                        visibility=visibility, config=config)
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
            else:
                hb_faces.extend(import_objects(rhino3dm_file, layer,
                    tolerance=model_tolerance))
    
    # If config is not provided
    else:
        for layer in rhino3dm_file.Layers:
            hb_faces.extend(import_objects(rhino3dm_file, layer,
                tolerance=model_tolerance))
    
    # Honeybee model name
    name = name or '.'.join(os.path.basename(path).split('.')[:-1])
    name = clean_string(name)

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
