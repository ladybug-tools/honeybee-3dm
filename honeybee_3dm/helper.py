"""A collection of general and config helper functions"""


from .material import mat_to_dict
from honeybee.face import Face
from honeybee.shade import Shade
from honeybee.aperture import Aperture
from honeybee.door import Door
from honeybee.facetype import face_types
from honeybee.typing import clean_and_id_string, clean_string


def get_unit_system(file_3dm):
    """Get units from a 3dm file object.

    Args:
        file_3dm: A Rhino3dm file object.

    Returns:
        Rhino3dm file unit as a string.
    """
    UNITS = ['Meters', 'Millimeters', 'Feet', 'Inches', 'Centimeters']

    try:
        file_unit = file_3dm.Settings.ModelUnitSystem
    except AttributeError:
        raise TypeError(f'Expected a Rhino 3dm file object not {type(file_3dm)}')

    unit = str(file_unit).split('.')[-1]

    if unit not in UNITS:
        raise ValueError(
            f'{unit} is not currently supported. Supported units are {UNITS}.'
        )

    return unit


def child_layer_control(config, layer_name):
    """Checks if child layers are requested for a layer in the config file.

    Args:
        config: A dictionary of the config settings.
        layer_name: A text string of the layer name

    Returns:
        A bool.
    """

    if 'include_child_layers' in config['layers'][layer_name] and \
            config['layers'][layer_name]['include_child_layers']:
        return True
    else:
        return False


def grid_controls(config, layer_name):
    """Returns grid controls for a layer from the config.

    Args:
        grid_controls: A list of grid controls from the config file

    Returns:
        A tuple of grid controls

        -   grid_size,
        -   grid_offset.
        
        if valid grid settings are found in the config file or None
    """

    if 'grid_settings' in config['layers'][layer_name] and \
            config['layers'][layer_name]['exclude_from_rad']:
        grid_controls = config['layers'][layer_name]['grid_settings']
        return grid_controls['grid_size'], grid_controls['grid_offset']


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
            config['layers'][parent_layer_name]['include_child_layers']:
        return True
    else:
        return False


def face3d_to_hb_face_with_face_type(config, face_obj, name, layer_name):
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


def face3d_to_hb_face_with_rad(config, face_obj, name, layer_name):
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
        A tuple of lists;

        -   Honeybee Aperture objects,
        -   Honeybee Shade objects,
        -   Honeybee Door objects.

        List will be empty if no objects are found for that Honeybee object.
    """

    hb_apertures, hb_doors, hb_shades = ([], [], [])

    obj_name = name or clean_and_id_string(layer_name)
    args = [clean_string(obj_name), face_obj]

    def hb_object(config, layer_name, hb_obj):
        if 'radiance_material' in config['layers'][layer_name]:
            radiance_modifiers = mat_to_dict(config['sources']['radiance_material'])
            hb_obj.properties.radiance.modifier = radiance_modifiers[config[
                'layers'][layer_name]['radiance_material']]
            return hb_obj
        else:
            return hb_obj

    if config['layers'][layer_name]['honeybee_face_object'] == 'aperture':
        hb_aperture = Aperture(*args)
        hb_aperture.display_name = args[0]
        hb_apertures.append(hb_object(config, layer_name, hb_aperture))

    elif config['layers'][layer_name]['honeybee_face_object'] == 'door':
        hb_door = Door(*args)
        hb_door.display_name = args[0]
        hb_doors.append(hb_object(config, layer_name, hb_door))

    elif config['layers'][layer_name]['honeybee_face_object'] == 'shade':
        hb_shade = Shade(*args)
        hb_shade.display_name = args[0]
        hb_shades.append(hb_object(config, layer_name, hb_shade))

    return hb_apertures, hb_doors, hb_shades
