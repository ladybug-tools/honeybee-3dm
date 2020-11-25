"""A collection of helper functions."""
import json
from enum import Enum, unique

@unique
class HB_layers(Enum):
    """Default Honeybee layers.
    
    This class hosts all the default Honeybee layers in
    layer key : layer name structure

    Args:
        Enum: An Enum object.
    """
    grid = 'HB_grid'
    room = 'HB_room'
    wall = 'HB_wall'
    roof = 'HB_roof'
    floor = 'HB_floor'
    airwall = 'HB_airwall'
    shade = 'HB_shade'
    aperture = 'HB_aperture'
    door = 'HB_door'
    view = 'HB_view'


def read_json(path):
    """Get a dictionary from a config.json file.

    Args:
        path: A text string for the path to the config.json.

    Returns:
        A dictionary for the config.json
    """
    with open(path) as fh:
        config = json.load(fh)
        return config


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


def check_layer_in_hb_layers(config, layer_name):
    """Check whether a layer is tied to one of the HB_layers in the config file.

    Args:
        config: A dictionary. Config file in the form of a dictionary.
        layer_name: A text string. Layer name for the layer to run this check on.

    Returns:
        A bool. True if the layer is found tied to one of the HB_layers in the config
            file.
    """
    if layer_name in config['HB_layers'].values() \
        and layer_name != config['HB_layers']['HB_grid'] \
        and layer_name != config['HB_layers']['HB_room'] \
        and layer_name != config['HB_layers']['HB_view']:
        return True
    else:
        return False


def check_layer_not_in_hb_layers(config, layer_name, child_parent):
    """Check whether a layer pair is tied to one of the HB_layers in the config file.

    Check whether a layer and its parent are tied to one of the HB layers in the config
    file.

    Args:
        config: A dictionary. Config file in the form of a dictionary.
        layer_name: A text string. Layer name for the layer to run this check on.
        child_parent: A dictionary. A dictionary with child layer to parent layer 
            structure

    Returns:
        A bool. True if the layer and its parent layer are not found tied
            to one of the HB_layers in the config file.
    """
    if layer_name != config['HB_layers']['HB_grid'] \
        and layer_name != config['HB_layers']['HB_room'] \
        and layer_name != config['HB_layers']['HB_view'] \
        and child_parent[layer_name] != config['HB_layers']['HB_grid']:
        return True
    else:
        return False


def parent_child_layers(file_3dm, layer_name, visibility=True):
    """Get a list of parent and child layers for a layer.

    Args:
        file_3dm: A rhino3dm file object
        layer_name: Text string of a layer name.
        visibility: Bool. If set to False then the objects on an "off"
            layer in Rhino3dm will also be imported. Defaults to True.

    Returns:
        A list of parent and child layer names.
    """
    layer_names = []
    for layer in file_3dm.Layers:
        if visibility:
            if layer.Visible:
                parent_children = layer.FullPath.split('::')
                if layer_name in parent_children:
                    layer_names += parent_children
        else:
            parent_children = layer.FullPath.split('::')
            if layer_name in parent_children:
                layer_names += parent_children
    
    # remove duplicate layer names
    layer_names = list(set(layer_names))
    return layer_names


def child_parent_dict(file_3dm):
    """Get a dictionary with child layer and parent layer structure.

    Args:
        file_3dm: A rhino3dm file object

    Returns:
        A a dictionary with child layer and parent layer structure.
    """

    # name_index = {layer.Name: layer.Index for layer in file_3dm.Layers}
    child_parent_dict = {}

    for layer in file_3dm.Layers:
        parent_children = layer.FullPath.split('::')
        child_parent_dict[parent_children[-1]] = parent_children[0]

    return child_parent_dict


def objects_on_layer(file_3dm, layer, visibility=True):
    """Get a list of objects on child layers.

    Args:
        file_3dm: Input Rhino3DM object.
        layer: A Rhino3dm layer object.
        visibility: Bool. If set to False then the objects on an "off"
            layer in Rhino3dm will also be imported. Defaults to True.

    Returns:
        A list of Rhino3dm objects on a layer.
    """
    if visibility:
        if layer.Visible:
            layer_index = [layer.Index]
            return filter_objects_by_layer_index(file_3dm, layer_index)
        else:
            return []
    else:
        layer_index = [layer.Index]
        return filter_objects_by_layer_index(file_3dm, layer_index)
        
        
def objects_on_parent_child(file_3dm, layer_name, visibility=True):
    """Get all the objects on a layer and its sub-layers.

    Args:
        file_3dm: Input Rhino3DM object.
        layer_name: Rhino layer name.
        visibility: Bool. If set to False then the objects on an "off"
            layer in Rhino3dm will also be imported. Defaults to True.

    Returns:
        A list of Rhino3dm objects.
    """
    # Get a list of parent and child layers for the layer_name
    parent_child = parent_child_layers(file_3dm, layer_name, visibility)
    if parent_child:
        # Get Indexes for all layers
        if visibility:
            layer_index = [layer.Index for layer in file_3dm.Layers
                if layer.Name in parent_child and layer.Visible]
        else:
            layer_index = [layer.Index for layer in file_3dm.Layers
                if layer.Name in parent_child]
        if not layer_index:
            raise ValueError(f'Find no layer named "{layer_name}"')
    else:
        return []
    # Return a list of object on layer_name and its child layers
    return filter_objects_by_layer_index(file_3dm, layer_index)


def filter_objects_by_layer_index(file_3dm, layer_index):
    """Get all the objects in a layer.

    Args:
        file_3dm: Input Rhino 3DM object.
        layer_index: A list of indexes for Rhino layers

    Returns:
        A list of Rhino3dm objects.
    """

    return [obj for obj in file_3dm.Objects for index in layer_index
        if obj.Attributes.LayerIndex == index]
