"""Validation and schema generation for the config file and helper functions."""

import enum
import json
import os
import rhino3dm

from pydantic import BaseModel, validator, Field
from typing import Dict

from .material import mat_to_dict
from honeybee.face import Face
from honeybee.shade import Shade
from honeybee.aperture import Aperture
from honeybee.door import Door
from honeybee.facetype import face_types
from honeybee.typing import clean_and_id_string, clean_string


class FaceObjects(str, enum.Enum):
    """List of acceptable string names for Honeybee Classes."""
    door = 'door'
    shade = 'shade'
    aperture = 'aperture'


class FaceType(str, enum.Enum):
    """List of acceptable string names for Honeybee face types."""
    wall = 'wall'
    roof = 'roof'
    floor = 'floor'
    airwall = 'airwall'


class GridSettings(BaseModel):
    """Config for the grid-settings."""

    grid_size: float = Field(
        1.0,
        description='Grid spacing.'
    )

    grid_offset: float = Field(
        0.0,
        description='Grid offset'
    )

    @validator('grid_size')
    def check_grid_size(cls, v):
        grid_size = v
        if grid_size <= 0.0:
            raise ValueError('Grid size must be greater than zero.')
        return v


class LayerConfig(BaseModel):
    """Config for layer keys."""

    exclude_from_rad: bool = Field(
        False,
        description='Boolean to indicate if this layer should be excluded from '
        'radiance model.'
    )

    include_child_layers: bool = Field(
        False,
        description='Boolean to indicate if objects from child layers are to be imported'
    )

    radiance_material: str = Field(
        None,
        description='Text string of the radiance identifier.'
    )

    grid_settings: GridSettings = Field(
        None
    )

    honeybee_face_object: FaceObjects = Field(
        None,
        description='A text string for FaceObject to create either a Honeybee Shade,'
        ' a Honeybee door, or a Honeybee aperture object.'
    )

    honeybee_face_type: FaceType = Field(
        None,
        description='A text string for FaceType to create either a Honeybee Wall,'
        ' a Honeybee Floor, or a Honeybee aperture roof/ceiling, or a Honeybee.'
        ' Floor.'
    )


class Config(BaseModel):
    """Config for the config file."""

    sources: Dict[str, str] = Field(
        None,
        description='Path to the radiance .mat file.'
    )

    layers: Dict[str, LayerConfig] = Field(
        description='names of layer in rhino.'
    )

    @validator('sources')
    def check_sources(cls, v):
        sources = list(v.keys())
        if len(sources) != 1:
            raise ValueError('sources can only have one key.')

        if sources[0] != 'radiance_material':
            raise ValueError(
                    f'invalid sources key: {sources[0]}.'
                    'key must be radiance_material'
            )
        return v
    
    @validator('layers')
    def check_layers(cls, v):
        layers = list(v.keys())
        if not layers:
            raise ValueError('The config file cannot be used without layer names.')
        return v


def read_json(config_path):
    """Get a dictionary from a config.json file.

    Args:
        path: A text string for the path to the config.json.

    Returns:
        A dictionary for the config.json
    """
    try:
        with open(config_path) as fh:
            config = json.load(fh)
    except json.decoder.JSONDecodeError:
        raise ValueError(
            'Not a valid config file.'
        )
    return config


def check_layers(file_3dm, config):
    """Checks if layers in the config file are layers from the rhino file.

    Args:
        file_3dm: A rhino3dm file object.
        config: Config dictionary.

    Raises:
        KeyError: If any of the layer names mentioned in the config file is not found
            in the layers in the rhino file.

    Returns:
        Boolean value of True if no error is raised.
    """
    layers = [layer.Name for layer in file_3dm.Layers]
    layer_check = [True for layer in config['layers'] if layer in layers]
    if len(config['layers']) != layer_check.count(True):
        raise KeyError(
            'Only layer names from the Rhino file are allowed in the config file.'
        )
    else:
        return True


def check_rad(config):
    """Checks if radiance modifiers can be applied to objects on rhino layers.

    Args:
        config: Config dictionary.

    Raises:
        OSError: If the path to the radiance material file is not a valid path.
        KeyError: If the config file does not have a key named "radiance_material" in
            sources and a radiance material is requested in one of the layers in the
            config file.
        ValueError: If any of the radiance identifiers mentioned in the config file 
            are not found in the radiance materials file or do not match the identifiers
            in the radiance material file.

    Returns:
        Boolean value of True if no error is raised.
    """

    # Check-04: Check if radiance modifiers can be imported
    for layer in config['layers']:
        if 'radiance_material' in config['layers'][layer]:
            break
        if 'sources' in config and config['sources']['radiance_material']:
            os.path.isfile(config['sources']['radiance_material'])
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
            ' also found in the radiance material file and names of radiance'
            ' materials in the config file match the radiance identifiers in the'
            ' radiance material file.'
        )
    else:
        pass

    return True


def check_config(file_3dm, config_path):
    """Validates the config file and returns it in the form of a dictionary.

    Args:
        file_3dm: A rhino3dm file object.
        config_path: A text string for the path to the config file.

    Returns:
        Config dictionary or None if any of the checks fails.
    """
    # Validate against schema
    Config.parse_file(config_path)

    # Get a config dictionary from the config file
    config = read_json(config_path)

    # Validate config with external binaries
    if check_layers(file_3dm, config) and check_rad(config):
        return config
    else:
        None



def child_layer_control(config, layer_name):
    """Checks if child layers are requested for a layer in the config file."""

    if 'include_child_layers' in config['layers'][layer_name] and \
        config['layers'][layer_name]['include_child_layers'] == True:
        return True
    else:
        return False


def grid_controls(config, layer_name):
    """Returns grid controls for a layer from the config.

    Args:
        grid_controls: A list of grid controls from the config file

    Returns:
        A tuple of grid controls (grid_size, grid_offset) if valid 
            grid settings are found in the config file or None
    """

    if 'grid_settings' in config['layers'][layer_name] and \
            config['layers'][layer_name]['exclude_from_rad']:
        grid_controls = config['layers'][layer_name]['grid_settings']
        return grid_controls['grid_size'], grid_controls['grid_offset']
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
        config['layers'][parent_layer_name]['include_child_layers'] == True:
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
