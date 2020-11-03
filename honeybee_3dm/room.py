"""Creating Honeybee Room objects from rhino3dm closed volumes"""

# The Rhino3dm library provides the ability to access content of a Rhino3dm
# file from outside of Rhino
import rhino3dm

# The uuid library is used to create names for Honeybee object when a name
# is not assigned by a user
import uuid

# Importing dependencies from Honeybee-3dm package
from .togeometry import brep_to_face3d, extrusion_to_face3d, mesh_to_face3d
from .tojson import to_json

# Importing core Honeybee & Ladybug Geometry dependencies
from honeybee.room import Room
from honeybee.facetype import get_type_from_normal
from honeybee.typing import clean_and_id_string
from ladybug_geometry.geometry3d.face import Face3D
from ladybug_geometry.geometry3d.polyface import Polyface3D


def to_room(path):
    """This function looks up a rhino3dm file, converts the objects
    on the layer name "room" to Honeybee Room objects, and writes them
    to a json file.

    Args:
        path (A string): The path to the rhino file
    """
    # TODO create a quality check for the file path

    # Creating a rhino3dm object from the file at the path provided
    rhino3dm_file = rhino3dm.File3dm.Read(path)
    tolerance = rhino3dm_file.Settings.ModelAbsoluteTolerance

    # Gathering layer information from the rhino file
    layers = rhino3dm_file.Layers
    layer_name = [layer.Name for layer in layers]
    layer_index = [layer.Index for layer in layers]
    layer_dict = dict(zip(layer_name, layer_index))

    # Gathering breps / extrusions / closed meshes in the rhino file to create rooms
    volumes = [object for object in rhino3dm_file.Objects if object.Attributes.LayerIndex ==
               layer_dict["room"]]

    # Checking if all the rooms are either an extrusion, or a brep, or
    # a mesh and are closed volumes
    check = []
    for geo in volumes:
        geo = geo.Geometry
        if geo.ObjectType == rhino3dm.ObjectType.Extrusion and geo.IsSolid == True:
            check.append(True)
        if geo.ObjectType == rhino3dm.ObjectType.Brep and geo.IsSolid == True:
            check.append(True)
        if geo.ObjectType == rhino3dm.ObjectType.Mesh and geo.IsClosed == True:
            check.append(True)

    # Check if all the rhino3dm objects on the layer "room" are closed volumes
    assert (len(check) == len(
        volumes)), 'On the "rooms" layer, you must only have either closed brep,' \
        'or closed extrusions, closed meshes.' \
        ' Please make this change in the rhino file and try again'

    # Creating room names
    room_names = []
    for count, geo in enumerate(volumes):
        # If there's a user defined name of the object in rhino3dm, use it
        if len(geo.Attributes.Name) > 0:
            room_names.append(geo.Attributes.Name)
        # Else, generate a unique name
        else:
            name = "Room" + str(uuid.uuid4())[:8]
            room_names.append(name)

    # All the Honeybee Room objects will be collected here
    hb_rooms = []

    # For every closed volume on layer "room"
    for i in range(len(volumes)):
        rh_solid = volumes[i].Geometry
        # If it's a Brep, create Ladybug Face3D objects from it
        if rh_solid.ObjectType == rhino3dm.ObjectType.Brep:
            lb_faces = brep_to_face3d(rh_solid)
        # If it's an Extrusion, create Ladybug Face3D objects from it
        if rh_solid.ObjectType == rhino3dm.ObjectType.Extrusion:
            lb_faces = extrusion_to_face3d(rh_solid)
        # If it's a Mesh, create Ladybug Face3D objects from it
        if rh_solid.ObjectType == rhino3dm.ObjectType.Mesh:
            lb_faces = mesh_to_face3d(rh_solid)

        # Create Ladybug Polyface3D object from Ladybug Face3D objects
        lb_polyface = Polyface3D.from_faces(lb_faces, tolerance)
        name = room_names[i]
        # Create Honeybee Room object from Ladybug Polyface3D object
        hb_room = Room.from_polyface3d(name, lb_polyface)
        hb_rooms.append(hb_room)

    return hb_rooms
