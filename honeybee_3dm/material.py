"""Functions to work with the radiance material file"""

from honeybee_radiance.modifier.material import Plastic, Glass, BSDF, Mirror


def to_string(str_lst):
    """Get a joined string from a list of strings.

    Args:
        str_lst: A list of strings

    Returns:
        A string.
    """
    mat_string = ''
    for string in str_lst:
        mat_string += string
    return mat_string


def mat_to_dict(path):
    """Create a dictionary from a .mat file.

    This function reads every material in the .mat file and outputs a dictionary
    with a identifier : modifier structure.

    Args:
        path: A text string for the path to the .mat file
        
    Returns:
        A dictionary with radiance identifier to radiance modifier mapping.
    """
    try:
        with open(path) as fh:
            lines = fh.readlines()
    except Exception as e:
        raise ValueError(e)
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
