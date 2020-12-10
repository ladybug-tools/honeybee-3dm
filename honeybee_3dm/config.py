"""Config file schema and validation."""

import enum
import json
import os

from pydantic import BaseModel, validator, Field
from typing import Dict, Optional

from .material import mat_to_dict


class FaceObject(str, enum.Enum):
    """List of acceptable string names for Honeybee Face object types."""
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
        gt=0,
        description='Grid spacing to control grid density.'
    )

    grid_offset: float = Field(
        0.0,
        description='Offset to move grid away from the parent face by certain distance.'
    )


class LayerConfig(BaseModel):
    """Config for layer keys."""

    exclude_from_rad: Optional[bool] = Field(
        description='Boolean to indicate if this layer should be excluded from '
        'radiance model.'
    )

    include_child_layers: Optional[bool] = Field(
        description='Boolean to indicate if objects from child layers are to be imported.'
    )

    radiance_material: Optional[str] = Field(
        description='The name of radiance modifier.'
    )

    grid_settings: Optional[GridSettings] = Field(
        description='Grid settings for the layer.'
    )

    honeybee_face_object: Optional[FaceObject] = Field(
        description='A text string for FaceObject to create either a Honeybee Shade,'
        ' a Honeybee Door, or a Honeybee Aperture object.'
    )

    honeybee_face_type: Optional[FaceType] = Field(
        description='A text string for FaceType to create either a Honeybee Wall,'
        ' a Honeybee Floor, a Honeybee Roof/Ceiling, or a Honeybee Airwall.'
    )


class Config(BaseModel):
    """Config file."""

    sources: Dict[str, str] = Field(
        None,
        description='Path to input sources. Currently, the config only supports'
            ' "radiance_material" to indicate the path to the radiance.mat file.'
        )

    layers: Dict[str, LayerConfig] = Field(
        description='A dictionary to indicate the config for each layer in rhino 3dm'
            ' file. The key must be a Rhino layer name and the values must be a'
            ' LayerConfig.'
        )

    @validator('sources')
    def check_sources(cls, v):
        sources = list(v.keys())
        if len(sources) != 1:
            raise ValueError('sources can only have one key.')

        if sources[0] != 'radiance_material':
            raise ValueError(
                    f'invalid sources key: {sources[0]}.'
                    'key must be radiance_material.'
            )

        return v
    

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

    layer_check = [layer for layer in config['layers'] if layer not in layers]
    if layer_check:
        raise KeyError(
            'Only layer names from the Rhino file are allowed in the config file.'
            f'Found invalid layer names: {layer_check}'
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

    # Check if radiance modifiers can be imported
    radiance = False
    for layer in config['layers']:
        if 'radiance_material' in config['layers'][layer]:
            radiance = True
            break
    if radiance:
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
    else:
        pass
    
    # Check if all the radiance materials are found in the .mat file
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
    try:
        with open(config_path) as fh:
            config = json.load(fh)
    except json.decoder.JSONDecodeError:
        raise ValueError(
            'Not a valid json file.'
            )
    else:
        # Validate against schema
        config_obj = Config.parse_file(config_path)
        config = config_obj.dict(exclude_none=True)
        
        # Validate config with external binaries
        if check_layers(file_3dm, config) and check_rad(config):
            return config
        else:
            raise ValueError(
                'Config file could not be loaded. Please make sure it is a valid'
                ' config file.'
                )
