import rhino3dm
import uuid
from togeometry import to_face3d
from tojson import publish_json

try:  # import the core honeybee dependencies
    from honeybee.face import Face
    from honeybee.facetype import face_types
    from honeybee.boundarycondition import boundary_conditions
    from honeybee.typing import clean_and_id_string
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


# Gathering layer information from the rhino file
layers = file.Layers
layer_name = [layer.Name for layer in layers]
layer_index = [layer.Index for layer in layers]
layer_dict = dict(zip(layer_name, layer_index))


# Gathering surfaces / extrusions / meshes in the rhino file to create honeybee
# surfaces
faces = [object for object in file.Objects if object.Attributes.LayerIndex ==
         layer_dict["wall_interior"]]

# Creating face names
face_names = []
for count, geo in enumerate(faces):
    if len(geo.Attributes.Name) > 0:
        face_names.append(geo.Attributes.Name)
    else:
        name = "wall" + str(uuid.uuid4())[:8]
        face_names.append(name)

# Honeybee faces will be collected here
hb_faces = []
# for each rhino geometry selected
for i in range(len(faces)):
    face = faces[i].Geometry
    lb_face = to_face3d(face)[0]
    # print(isinstance(lb_face, Face3D))
    hb_face = Face(clean_and_id_string('{}_{}'.format(
        face_names[i], i)), lb_face)
    hb_face.display_name = '{}_{}'.format(face_names[i], i)
    hb_faces.append(hb_face)


publish_json(hb_faces)
