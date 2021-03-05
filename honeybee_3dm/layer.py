"""Functions to work with layers in a rhino file."""


def child_parent_dict(file_3dm):
    """Get a dictionary with child layer name and parent layer name structure.

    Args:
        file_3dm: A rhino3dm file object

    Returns:
        A a dictionary with child layer name and parent layer name structure.
    """
    child_parent_dict = {}

    for layer in file_3dm.Layers:
        parent_children = layer.FullPath.split('::')
        child_parent_dict[parent_children[-1]] = parent_children[0]

    return child_parent_dict


def parent_child_layers(file_3dm, layer_name):
    """Get a list of parent and child layers for a layer.

    Args:
        file_3dm: A rhino3dm file object
        layer_name: Text string of a layer name.
        
    Returns:
        A list of parent and child layer names.
    """
    layer_names = []
    for layer in file_3dm.Layers:
        parent_children = layer.FullPath.split('::')
        if layer_name in parent_children:
            layer_names += parent_children

    return list(set(layer_names))


def filter_objects_by_layer_index(file_3dm, layer_index):
    """Get all the objects in a layer based on layer index.

    Args:
        file_3dm: Input Rhino 3DM object.
        layer_index: A list of indexes for Rhino layers

    Returns:
        A list of Rhino3dm objects.
    """

    return [obj for obj in file_3dm.Objects for index in layer_index
            if obj.Attributes.LayerIndex == index and obj.Attributes.Visible]


def objects_on_parent_child(file_3dm, layer_name):
    """Get all the objects on a layer and its child-layers.

    Args:
        file_3dm: Input Rhino3DM object.
        layer_name: Rhino layer name.

    Returns:
        A list of Rhino3dm objects on the layer and its child layers.
    """
    # Get a list of parent and child layers for the layer_name
    parent_child = parent_child_layers(file_3dm, layer_name)

    layer_index = [
        layer.Index for layer in file_3dm.Layers if layer.Name in parent_child]
    if not layer_index:
        raise ValueError(f'Find no layer named "{layer_name}"')

    return filter_objects_by_layer_index(file_3dm, layer_index)


def objects_on_layer(file_3dm, layer):
    """Get a list of objects on a layer.

    Args:
        file_3dm: Input Rhino3DM object.
        layer: A Rhino3dm layer object.

    Returns:
        A list of Rhino3dm objects on a layer.
    """
    layer_index = [layer.Index]
    return filter_objects_by_layer_index(file_3dm, layer_index)


def visible_layers(file_3dm):
    """Get a list of visible layers in the rhino file.

    This function mimics layer visibilty in rhino. Only layers that are "on" in rhino
    are considered visible layers.

    Args:
        file_3dm: A rhino3dm file object.

    Returns:
        A list of rhino3dm layer objects for all the layers visible in rhino
    """
    visible_layers = []

    layer_name_to_layer = {layer.Name: layer for layer in file_3dm.Layers}

    for layer in file_3dm.Layers:
        layer_parent = layer.FullPath.split('::')
        visibility_check = [
            False if not layer_name_to_layer[layer_name].Visible
            else True for layer_name in layer_parent]
        if visibility_check.count(False) == 0:
            visible_layers.append(layer)
        else:
            pass
    
    return visible_layers
    