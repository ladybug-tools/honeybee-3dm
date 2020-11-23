"""A collection of helper functions."""


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


def parent_child_layers(file_obj, layer_name):
    """Get a list of parent and child layers for a layer.

    Args:
        file_obj: A rhino3dm file object
        layer_name: Text string of a layer name.

    Returns:
        A list of parent and child layer names.
    """
    layer_names = []
    for layer in file_obj.Layers:
        if layer.Visible:
            parent_children = layer.FullPath.split('::')
            if layer_name in parent_children:
                layer_names += parent_children
    
    # remove duplicate layer names
    layer_names = list(dict.fromkeys(layer_names))
    return layer_names


def parent_child_index(file_obj, layer_lst):
    """Get a dictionary with child layer : Parent Honeybee Layer structure.

    Args:
        file_obj: A rhino3dm file object
        layer_lst: A list of Honeybee layer names

    Returns:
        A a dictionary with child layer : Parent Honeybee Layer structure.
    """
    name_index = {layer.Name: layer.Index for layer in file_obj.Layers if layer.Visible}

    parent_child_dict = {}
    for layer_name in layer_lst:
        for layer in file_obj.Layers:
            if layer.Visible:
                parent_children = layer.FullPath.split('::')
                if layer_name in parent_children:
                    parent_child_dict[name_index[parent_children[-1]]] = name_index[parent_children[0]]
    
    return parent_child_dict


def filter_objects_by_layer(file_3dm, layer_name):
    """Get all the objects in a layer.

    Args:
        file_3dm: Input Rhino3DM object.
        layer_name: Rhino layer name.

    Returns:
        A list of Rhino3dm objects.
    """
    # Get a list of parent and child layers for the layer_name
    parent_child = parent_child_layers(file_3dm, layer_name)

    # Get Indexes for all layers
    layer_index = [layer.Index for layer in file_3dm.Layers if layer.Name in parent_child
        and layer.Visible]
    if not layer_index:
        raise ValueError(f'Find no layer named "{layer_name}"')

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


def filter_objects_by_layers(file_3dm, layer_names):
    """Get all the objects under a list of layers.

    The objects will be separated for each layer.
    Args:
        file_3dm: Input Rhino 3DM object.
        layer_names: A list of layer names in text.

    Returns:
        A list of lists. A sub-list for each of the layers in layer_names
    """
    # A dictionary with child layer index : Parent layer index structure
    # The parent layer is one of the Honeybee layers
    parent_child_dict = parent_child_index(file_3dm, layer_names)

    # get layer tables if the layer is in official Honeybee layers and is visible
    layer_table = {layer.Index: layer.Name for layer in file_3dm.Layers if layer.Visible}

    # create a place holder for each layer
    objects = {layer_name: [] for layer_name in layer_names}

    # get index for each layer
    for obj in file_3dm.Objects:
        index = obj.Attributes.LayerIndex
        try:
            # Get the Honeybee layer name if the object is on a child layer of 
            # one of the Honeybee layers
            layer_name = layer_table[parent_child_dict[index]]
            objects[layer_name].append(obj)
        # For an object that is not on either Honeybee layer or their child layers
        except KeyError:
            continue

    # return objects as a list of list based on the input layer_names order
    return [objects[layer_name] for layer_name in layer_names]
