import rhino3dm
import uuid
from togeometry import to_face3d
from tojson import publish_json

try:  # import the core honeybee dependencies
    from honeybee.face import Face
    from honeybee.shade import Shade
    from honeybee.aperture import Aperture
    from honeybee.door import Door
    from honeybee.facetype import face_types
    from honeybee.boundarycondition import boundary_conditions
    from honeybee.typing import clean_and_id_string
    from honeybee.facetype import face_types
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from ladybug_geometry.geometry3d.face import Face3D

except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))


try:  # import the honeybee-energy extension
    from honeybee_energy.lib.constructions import opaque_construction_by_identifier
except ImportError as e:
    if len(ep_constr_) != 0:
        raise ValueError('ep_constr_ has been specified but honeybee-energy '
                         'has failed to import.\n{}'.format(e))

try:  # import the honeybee-radiance extension
    from honeybee_radiance.lib.modifiers import modifier_by_identifier
except ImportError as e:
    if len(rad_mod_) != 0:
        raise ValueError('rad_mod_ has been specified but honeybee-radiance '
                         'has failed to import.\n{}'.format(e))


# The path here is the path to the rhinofile in .3dm format
path = "D:\Github\Work-in-Progress\RhinoToHBJSON\sample.3dm"
file = rhino3dm.File3dm.Read(path)


# Honeybee faces will be collected here
hb_faces = []

# Gathering layer information from the rhino file
layers = file.Layers
# Layer names in the Rhino file
layer_names = [layer_name.Name for layer_name in layers]
# Layer Indexes for the layers in the Rhino file
layer_indexes = [layer_name.Index for layer_name in layers]
# A dictionary with the layer names as keys and layer indexes as values
layer_dict = dict(zip(layer_names, layer_indexes))


def layer_name_to_hb_objects(layer):
    """This function takes a Rhino layer and spits out a Honeybee face type
    and Honeybee Class to be used for Rhino to Honeybee translation.

    Args:
        layer (A string): Name of the Rhino layer

    Returns:
        hb_type: A Honeybee face type object
        hb_face_module: A Honeybee class. It is either of Face, Shade, Aperture, or Door
    """
    hb_type = " "  # Variable holding a Honeybee face type
    hb_face_module = " "  # Variable holding a Honeybee module name

    if layer == "roof":
        hb_type = face_types.roof_ceiling
        hb_face_module = Face
    if layer == "wall":
        hb_type = face_types.wall
        hb_face_module = Face
    if layer == "floor":
        hb_type = face_types.floor
        hb_face_module = Face
    if layer == "airwall":
        hb_type = face_types.air_boundary
        hb_face_module = Face
    if layer == "shade":
        hb_type = None
        hb_face_module = Shade
    if layer == "aperture":
        hb_type = None
        hb_face_module = Aperture
    if layer == "door":
        hb_type = None
        hb_face_module = Door
    if layer == "Default":
        pass

    return (hb_type, hb_face_module)


# Look at Rhino layers and
for layer in layer_names:
    hb_face_type = layer_name_to_hb_objects(layer)[0]
    hb_face_module = layer_name_to_hb_objects(layer)[1]
    layer_name = layer

    # Gathering planar geometries from the Rhino layer
    rhino_faces = [object for object in file.Objects if object.Attributes.LayerIndex ==
                   layer_dict[layer_name]]

    # Creating face names
    face_names = []
    for count, geo in enumerate(rhino_faces):
        # If there's a user given name, use it
        # TODO: Quality check for user input name will have to be created here
        if len(geo.Attributes.Name) > 0:
            face_names.append(geo.Attributes.Name)
        # Use auto generated name
        else:
            name = layer_name + str(uuid.uuid4())[:8]
            face_names.append(name)

    # for each rhino geometry gathered
    for i in range(len(rhino_faces)):
        face = rhino_faces[i].Geometry
        # Converting the Rhino3dm geometry into a Ladybug Face3D object
        lb_face = to_face3d(face)
        for j in range(len(lb_face)):
            # Converting Ladybug Face3D into Honeybee Face
            if hb_face_module == Face:
                hb_face = hb_face_module(clean_and_id_string('{}_{}'.format(
                    face_names[i], i)), lb_face[j], hb_face_type)
            if hb_face_module == Shade:
                hb_face = hb_face_module(clean_and_id_string(
                    '{}_{}'.format(face_names[i], i)), lb_face[j])
            if hb_face_module == Aperture:
                hb_face = hb_face_module(clean_and_id_string(
                    '{}_{}'.format(face_names[i], i)), lb_face[j])
            if hb_face_module == Door:
                hb_face = hb_face_module(clean_and_id_string(
                    '{}_{}'.format(face_names[i], i)), lb_face[j])
            # Assigning a name to the Honeybee Face
            hb_face.display_name = '{}_{}'.format(face_names[i], i)
            hb_faces.append(hb_face)

# Write the Honeybee faces in a JSON file
publish_json(hb_faces)
