"""Functions to work with layers in a rhino file."""


def child_parent_dict(file_3dm):
    """Get a dictionary with child layer and parent layer structure.

    Args:
        file_3dm: A rhino3dm file object

    Returns:
        A a dictionary with child layer and parent layer structure.
    """
    child_parent_dict = {}

    for layer in file_3dm.Layers:
        parent_children = layer.FullPath.split('::')
        child_parent_dict[parent_children[-1]] = parent_children[0]

    return child_parent_dict


def parent_child_layers(file_3dm, layer_name, layer_visibility=True):
    """Get a list of parent and child layers for a layer.

    Args:
        file_3dm: A rhino3dm file object
        layer_name: Text string of a layer name.
        layer_visibility: Bool. If set to False then the objects on an "off"
            layer in Rhino3dm will also be imported. Defaults to True.

    Returns:
        A list of parent and child layer names.
    """
    layer_names = []
    for layer in file_3dm.Layers:
        if layer_visibility:
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


def objects_on_parent_child(file_3dm, layer_name, layer_visibility=True):
    """Get all the objects on a layer and its child-layers.

    Args:
        file_3dm: Input Rhino3DM object.
        layer_name: Rhino layer name.
        layer_visibility: Bool. If set to False then the objects on an "off"
            layer in Rhino3dm will also be imported. Defaults to True.

    Returns:
        A list of Rhino3dm objects.
    """
    # Get a list of parent and child layers for the layer_name
    parent_child = parent_child_layers(file_3dm, layer_name, layer_visibility)
    if parent_child:
        # Get Indexes for all layers
        if layer_visibility:
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


def objects_on_layer(file_3dm, layer, layer_visibility=True):
    """Get a list of objects on a layer.

    Args:
        file_3dm: Input Rhino3DM object.
        layer: A Rhino3dm layer object.
        layer_visibility: Bool. If set to False then the objects on an "off"
            layer in Rhino3dm will also be imported. Defaults to True.

    Returns:
        A list of Rhino3dm objects on a layer.
    """
    if layer_visibility:
        if layer.Visible:
            layer_index = [layer.Index]
            return filter_objects_by_layer_index(file_3dm, layer_index)
        else:
            return []
    else:
        layer_index = [layer.Index]
        return filter_objects_by_layer_index(file_3dm, layer_index)