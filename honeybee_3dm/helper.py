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


def filter_objects_by_layer(file_3dm, layer_name):
    """Get all the objects in a layer.

    Args:
        file_3dm: Input Rhino3DM object.
        layer_name: Rhino layer name.

    Returns:
        A list of Rhino3dm objects.
    """
    layer_index = [layer.Index for layer in file_3dm.Layers if layer.Name == layer_name]
    if not layer_index:
        raise ValueError(f'Find no layer named "{layer_name}"')

    return filter_objects_by_layer_index(file_3dm, layer_index[0])


def filter_objects_by_layer_index(file_3dm, layer_index):
    """Get all the objects in a layer.

    Args:
        file_3dm: Input Rhino 3DM object.
        layer_index: Index of a Rhino layer.

    Returns:
        A list of Rhino3dm objects.
    """

    return [obj for obj in file_3dm.Objects if obj.Attributes.LayerIndex == layer_index]


def filter_objects_by_layers(file_3dm, layer_names):
    """Get all the objects under a list of layers.

    The objects will be separated for each layer.
    Args:
        file_3dm: Input Rhino 3DM object.
        layer_names: A list of layer names in text.

    Returns:
        A list of lists. A sub-list for each of the layers in layer_names
    """
    # get layer tables
    layer_table = {layer.Index: layer.Name for layer in file_3dm.Layers}

    # create a place holder for each layer
    objects = {layer_name: [] for layer_name in layer_names}

    # get index for each layer
    for obj in file_3dm.Objects:
        index = obj.Attributes.LayerIndex
        try:
            layer_name = layer_table[index]
            objects[layer_name].append(obj)
        except KeyError:
            # layer is not one of the input layer names
            continue

    # return objects as a list of list based on the input layer_names order
    return [objects[layer_name] for layer_name in layer_names]
