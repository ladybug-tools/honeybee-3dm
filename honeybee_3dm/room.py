import rhino3dm
import uuid

# * Importing core honeybee dependencies
try:
    from honeybee.room import Room
    from honeybee.facetype import get_type_from_normal
    from honeybee.typing import clean_and_id_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from ladybug_geometry.geometry3d.face import Face3D
    from ladybug_geometry.geometry3d.polyface import Polyface3D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))


# * The path here is the path to the rhinofile in .3dm format
path = "D:\Github\Work-in-Progress\RhinoToHBJSON\sample.3dm"
file = rhino3dm.File3dm.Read(path)


# * Gathering layer information from the rhino file
layers = file.Layers
layer_name = [layer.Name for layer in layers]
layer_index = [layer.Index for layer in layers]
layer_dict = dict(zip(layer_name, layer_index))


# * Gathering breps / extrusions / closed meshes in the rhino file to create rooms
volumes = [object for object in file.Objects if object.Attributes.LayerIndex ==
           layer_dict["rooms"]]

# Checking if all the rooms are either an extrusion, or a brep, or a mesh and are closed volumes
check = []
for geo in volumes:
    geo = geo.Geometry
    if geo.ObjectType == rhino3dm.ObjectType.Extrusion and geo.IsSolid == True:
        check.append(True)
    if geo.ObjectType == rhino3dm.ObjectType.Brep and geo.IsSolid == True:
        check.append(True)
    if geo.ObjectType == rhino3dm.ObjectType.Mesh and geo.IsClosed == True:
        check.append(True)

assert (len(check) == len(
    volumes)), 'On the "rooms" layer, you must only have either closed brep,' \
    'or closed extrusions, closed meshes.' \
    ' Please make this change in the rhino file and try again'


# Creating rooms
room_names = []
for count, geo in enumerate(volumes):
    if len(geo.Attributes.Name) > 0:
        room_names.append(geo.Attributes.Name)
    else:
        name = "Room" + str(uuid.uuid4())[:8]
        room_names.append(name)

    og = geo.Geometry
    if og.ObjectType == rhino3dm.ObjectType.Extrusion:
        og = og.ToBrep(True)
    faces = og.Faces
    ladybug_faces = Polyface3D.from_faces(faces, 0.01)

    room = Room.from_polyface3d(
        name, ladybug_faces, roof_angle=30, ground_depth=0)
    # room.display_name = name
print(room_names)

