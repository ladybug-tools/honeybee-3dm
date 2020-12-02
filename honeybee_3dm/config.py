"""Functions to work with the config file."""

import json
import os

from honeybee.face import Face
from honeybee.shade import Shade
from honeybee.aperture import Aperture
from honeybee.door import Door
from honeybee.facetype import face_types
from honeybee.typing import clean_and_id_string, clean_string
from .material import mat_to_dict


def read_json(path):
    """Get a dictionary from a config.json file.

    Args:
        path: A text string for the path to the config.json.

    Returns:
        A dictionary for the config.json
    """
    try:
        with open(path) as fh:
            config = json.load(fh)
    except json.decoder.JSONDecodeError:
        raise ValueError(
            'Not a valid config file.'
        )
    return config


def child_layer_control(config, layer_name):
    """Checks if child layers are requested for a layer in the config file."""

    if 'include_child_layers' in config['layers'][layer_name] and \
        config['layers'][layer_name]['include_child_layers'].lower() == 'true':
        return True
    else:
        return False


def grid_controls(config, layer_name):
    """Checks grid controls from the config file and returns valid grid controls.

    Args:
        grid_controls: A list of grid controls from the config file

    Returns:
        A tuple of grid controls (grid-size-x, gris-size-y, grid-offset) if valid 
            grid settings are found in the config file or None
    """

    if 'grid_settings' in config['layers'][layer_name] and \
            'exclude_from_rad' in config['layers'][layer_name]:
        
        auth_grid_keys = ['grid-size-x', 'grid-size-y', 'grid-offset']
        grid_key_check = [True for key in config['layers'][layer_name]['grid_settings'] \
            if key in auth_grid_keys]

        if len(config['layers'][layer_name]['grid_settings']) == 3 and \
            grid_key_check.count(True) == 3:
            pass
        else:
            raise KeyError(
                f'The keys in grid-settings must be from {tuple(auth_grid_keys)}.'
                ' Other keys are not allowed.'
        )
        grid_controls = config['layers'][layer_name]['grid_settings']
        
        check = [isinstance(value, float) for value in grid_controls.values()]
        
        if len(grid_controls) == check.count(True):
            return (grid_controls['grid-size-x'], grid_controls['grid-size-y'],
                grid_controls['grid-offset'])
        else:
            raise ValueError(
                'Grid size and offset distance need to be decimal point numbers in'
                ' the config file. Please fix that and try again.'
            )
    else:
        return None


def check_parent_in_config(file_3dm, config, layer_name, parent_layer_name):
    """Checks if the parent layer of a layer is already mentioned in the config file.

    This function will return True if the parent layer of a layer is already mentioned
    in the config file and child layers are requested from that parent layer in the
    config file.

    Args:
        file_3dm: A rhino3dm file objects.
        config: A dictionary of the config settings.
        layer_name: A text string of the layer name
        parent_layer_name: A text string of the parent layer name

    Returns:
        A bool.
    """

    if parent_layer_name in config['layers'] and\
        'include_child_layers' in config['layers'][parent_layer_name] and\
        config['layers'][parent_layer_name]['include_child_layers'].lower() == 'true':
        return True
    else:
        return False


def face3d_to_face_type_to_hb_face(config, face_obj, name, layer_name):
    """Create a Honeybee Face object with a specific face_type.

    This function returns a Honeybee Face object with a specific face_type requested
    in the config file and also assign a radiance material to the face if requested
    from the config file.

    Args:
        config: A dictionary of the config settings.
        face_obj: A Ladybug Face3d object.
        name: A text string of the name of the rhino object.
        layer_name: A text string of the rhino layer name.

    Returns:
        A Honeybee Face object.
    """
    
    obj_name = name or clean_and_id_string(layer_name)
    args = [clean_string(obj_name), face_obj]
    
    if config['layers'][layer_name]['honeybee_face_type'] == 'roof':
        face_type = face_types.roof_ceiling
    
    elif config['layers'][layer_name]['honeybee_face_type'] == 'wall':
        face_type = face_types.wall
    
    elif config['layers'][layer_name]['honeybee_face_type'] == 'floor':
        face_type = face_types.floor
    
    elif config['layers'][layer_name]['honeybee_face_type'] == 'airwall':
        face_type = face_types.air_boundary
    
    args.append(face_type)
    hb_face = Face(*args)
    hb_face.display_name = args[0]
    
    if 'radiance_material' in config['layers'][layer_name]:
        radiance_modifiers = mat_to_dict(config['sources']['radiance_material'])
        hb_face.properties.radiance.modifier = radiance_modifiers[config
            ['layers'][layer_name]['radiance_material']]
        return hb_face
    else:
        return hb_face


def face3d_to_rad_to_hb_face(config, face_obj, name, layer_name):
    """Create a Honeybee Face object with a radiance material assigned to it.

    Args:
        config: A dictionary of the config settings.
        face_obj: A Ladybug Face3d object.
        name: A text string of the name of the rhino object.
        layer_name: A text string of the rhino layer name.

    Returns:
        A Honeybee Face object.
    """
    
    obj_name = name or clean_and_id_string(layer_name)
    args = [clean_string(obj_name), face_obj]
    hb_face = Face(*args)
    hb_face.display_name = args[0]
    
    if 'radiance_material' in config['layers'][layer_name]:
        radiance_modifiers = mat_to_dict(config['sources']['radiance_material'])
        hb_face.properties.radiance.modifier = radiance_modifiers[config
            ['layers'][layer_name]['radiance_material']]
        return hb_face
    else:
        return hb_face


def face3d_to_hb_object(config, face_obj, name, layer_name):
    """Create Honeybee Aperture, Shade, and Door objects.

    Args:
        config: A dictionary of the config settings.
        face_obj: A Ladybug Face3d object.
        name: A text string of the name of the rhino object.
        layer_name: A text string of the rhino layer name.

    Returns:
        A tuple of lists. Each list contains Honeybee Aperture objects, 
            Honeybee Shade objects, and Honeybee Door objects. List will 
            be empty if no objects are found for that Honeybee object.
    """

    hb_shades, hb_apertures, hb_doors = tuple([[] for _ in range(3)])

    obj_name = name or clean_and_id_string(layer_name)
    args = [clean_string(obj_name), face_obj]
    
    if config['layers'][layer_name]['honeybee_face_object'] == 'aperture':
        hb_aperture = Aperture(*args)
        hb_aperture.display_name = args[0]
        
        if 'radiance_material' in config['layers'][layer_name]:
            radiance_modifiers = mat_to_dict(config['sources']['radiance_material'])
            hb_aperture.properties.radiance.modifier = radiance_modifiers[config[
                'layers'][layer_name]['radiance_material']]
            hb_apertures.append(hb_aperture)
        else:
            hb_apertures.append(hb_aperture)
    
    elif config['layers'][layer_name]['honeybee_face_object'] == 'door':
        hb_door = Door(*args)
        hb_door.display_name = args[0]

        if 'radiance_material' in config['layers'][layer_name]:
            radiance_modifiers = mat_to_dict(config['sources']['radiance_material'])
            hb_door.properties.radiance.modifier = radiance_modifiers[config[
                'layers'][layer_name]['radiance_material']]
            hb_doors.append(hb_door)
        else:
            hb_doors.append(hb_door)

    elif config['layers'][layer_name]['honeybee_face_object'] == 'shade':
        hb_shade = Shade(*args)
        hb_shade.display_name = args[0]

        if 'radiance_material' in config['layers'][layer_name]:
            radiance_modifiers = mat_to_dict(config['sources']['radiance_material'])
            hb_door.properties.radiance.modifier = radiance_modifiers[config[
                'layers'][layer_name]['radiance_material']]
            hb_shades.append(hb_shade)
        else:
            hb_shades.append(hb_shade)

    return hb_apertures, hb_shades, hb_doors


def check_config(file_3dm, config):
    """Quality check for the config file.

    Args:
        file_3dm: A rhino3dm file object.
        config: A dictionary of the config settings.

    Raises:
        KeyError: KeyError will be raised if the key "layers" is not found in the config
            file.
        KeyError: KeyError will be raised if a layer in the config file is not found in 
            the rhino file.
        KeyError: KeyError will be raised if any of the key in a layer is not a valid
            key.
        ValueError: ValueError will be raised if a key has an empty string as a value.
        OSError: OSError will be raised if the path to radiance material file is not
            valid.
        KeyError: KeyError will be raised if the key "radiance_meterial" is not found
            in the "sources" and the key "radiance_material" is found in one of the 
            layers.
        ValueError: ValueError is raised if all the radiance materials requested in the
            config file are not found in the radiance material file.

    Returns:
        True if no error is raised.
    """

    # A list of layer names from the rhino file
    layers = [layer.Name for layer in file_3dm.Layers]

    # Check-01: If only rhino layers are used in the config
    if 'layers' not in config:
        raise KeyError(
            'layers not found in the config file.'
        )
    else:
        layer_check = [True for key in config['layers'] if key in layers]
        if len(config['layers']) != layer_check.count(True):
            raise KeyError(
                'The layer names in the "layers" do not match names of the layers in'
                ' rhino.'
            )
        else:
            pass
    
    # Check-02: If all the layer keys are authentic
    auth_keys = ['exclude_from_rad', 'grid_settings', 'include_child_layers',
        'radiance_material', 'honeybee_face_object', 'honeybee_face_type']
    
    unique_layer_keys = set([key for layer in config['layers'] for\
        key in config['layers'][layer]])
    layer_key_check = [True for key in unique_layer_keys if key in auth_keys]
    
    if len(unique_layer_keys) != layer_key_check.count(True):
        raise KeyError(
                f'The layer keys must be from {tuple(auth_keys)}'
            )
    else:
        pass

    # Check-03: Check if there are any blank values
    parent_value_check = [True for value in config.values() if value != " "]
    if len(config) != parent_value_check.count(True):
        raise ValueError(
                'Keys without values are not allowed in the config file'
            )
    else:
        child_value_check = [True if config['layers'][layer][key] != " " else False for\
            layer in config['layers'] for key in config['layers'][layer]]
        if len(child_value_check) != child_value_check.count(True):
            raise ValueError(
                'Keys without values are not allowed in the config file'
            )
        else:
            pass

    # Check-04: Check if radiance modifiers can be imported
    for layer in config['layers']:
        if 'radiance_material' in config['layers'][layer]:
            break
        if 'sources' in config and config['sources']['radiance_material']:
            os.path.isfile(config['sources']['radiance_material'])
            # Get the config file as a directory
            try:
                modifiers_dict = mat_to_dict(config['sources']['radiance_material'])
            except OSError:
                path = config['sources']['radiance_material']
                raise OSError(
                    f'The path {path} is not a valid path. Please try' 
                    ' using double backslashes in the  file path.'
                        )
        else:
            raise KeyError(
                'Please make sure the config file has the key "radiance_material" in'
                ' sources.'
        )
    
    # Check-05: Check if all the radiance materials are found in the .mat file
    rad_mat = [config['layers'][layer][key] for layer in config['layers'] for key \
        in config['layers'][layer] if key == 'radiance_material']
    
    rad_mat_check = [True for mat in rad_mat if mat in modifiers_dict]
    if len(rad_mat) != rad_mat_check.count(True):
        raise ValueError(
            'Please make sure all the radiance materials used in the config file are'
            ' also found in the radiance material file.'
        )
    else:
        pass

    return True
