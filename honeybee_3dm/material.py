"""Creating Honeybee model objects from rhino3dm surfaces and closed volumes"""

import warnings
from honeybee_radiance.modifier.material import Plastic, Glass, BSDF, Mirror


def to_string(str_lst):
    """Get a string from a list of strings.

    Args:
        str_lst: A list of strings

    Returns:
        A string.
    """
    mat_string = ''
    for str in str_lst:
        mat_string += str
    return mat_string


def mat_to_dict(path):
    """Create a dictionary from a .mat file.

    This function reads every material in the .mat file and outputs a dictionary
    with a identifier : modifier structure.

    Args:
        path: A text string for the path to the .mat file
    
    Returns:
        A dictionary with radiance identifier : modifier structure
    """
    try:
        with open(path) as fh:
            lines = fh.readlines()
    except Exception as e:
        warnings.warn(e)
    else:
        material_dict = {'plastic': Plastic,
                        'glass': Glass,
                        'mirror': Mirror,
                        'BSDF': BSDF}

        # Read all the materials from the .mat file
        materials = [lines[index:(index+4)] for index, line in enumerate(lines)
            if 'void' in line]
            
        # Convert text string of materials into Radiance modifiers
        modifiers = [material_dict[material[0].split(' ')[1]].from_string(
                to_string(material)) for material in materials]

        # Create a dictionary with identifier : modifier structure
        modifiers_dict = {modifier.identifier: modifier for modifier in modifiers}
        
        return modifiers_dict


def get_layer_modifier(file_3dm, modifiers_dict, layer):
    """Get a radiance modifier based on the material on a Rhino3dm layer.

    This function checks if a Rhino3dm layer has material property and 
    cross-references the material property with the modifiers in the .mat file.

    Args:
        file_3dm: A Rhino3dm file object
        modifiers_dict: A dictionary of radiance identifier : modifier structure
        layer: A Rhino3dm layer object.

    Returns:
        A Radiance modifier object or None if the material name on the Rhino layer
            does not match one of the radiance identifiers in the .mat or if a
            radiance modifier is not found in the .mat file for the material on a
            Rhino layer.
    """
    if modifiers_dict and layer.RenderMaterialIndex != -1:
        if file_3dm.Materials.FindIndex(layer.RenderMaterialIndex
            ).Name in modifiers_dict and ' ' not in file_3dm.Materials.FindIndex(
                layer.RenderMaterialIndex).Name:
            return modifiers_dict[
                file_3dm.Materials.FindIndex(layer.RenderMaterialIndex).Name
                ]
        else:
            warnings.warn(
                'Either a modifier with an exact same name is not found in the .mat file'
                f' or the Rhino layer "{layer.Name}"" has a material with no name.'
                ' or there is a white space in the material name.'
                ' Default Honeybee modifier will be applied.'
            )
            return None
    else:
        return None