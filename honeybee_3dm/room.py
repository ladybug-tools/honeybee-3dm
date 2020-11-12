"""Creating Honeybee Room objects from rhino3dm closed volumes"""

# The Rhino3dm library provides the ability to access content of a Rhino3dm
# file from outside of Rhino
import rhino3dm

# The uuid library is used to create names for Honeybee object when a name
# is not assigned by a user
import uuid

# Importing core Honeybee & Ladybug Geometry dependencies
from honeybee.room import Room
from honeybee.facetype import get_type_from_normal
from honeybee.typing import clean_and_id_string
from ladybug_geometry.geometry3d.face import Face3D
from ladybug_geometry.geometry3d.polyface import Polyface3D

# Importing dependencies from Honeybee-3dm package
from .togeometry import brep_to_face3d, extrusion_to_face3d, mesh_to_face3d


def to_room(rhino3dm_file, tolerance):
    """Creates Honeybee faces from a rhino3dm file.

    This function looks up a rhino3dm file, converts the objects
    on the layer name "room" to Honeybee Room objects, and writes them
    to a json file.

    Args:
        rhino3dm_file: The rhino file from which Honeybee faces will be created.
        tolerance: A rhino3dm tolerance object. Tolerance set in the rhino file.

    Returns:
        A list of Honeybee rooms.
    """
    layer_dict = {
        layer.Name: layer.Index for layer in rhino3dm_file.Layers}

    # Getting all the objects on the layer named "room"
    volumes = [obj for obj in rhino3dm_file.Objects if obj.Attributes.LayerIndex ==
               layer_dict["room"]]

    # From all the objects on the layer named "room" take only solid objects
    check = []
    for geo in volumes:
        geo = geo.Geometry
        if geo.ObjectType == rhino3dm.ObjectType.Extrusion and geo.IsSolid == True:
            check.append(True)
        elif geo.ObjectType == rhino3dm.ObjectType.Brep and geo.IsSolid == True:
            check.append(True)
        elif geo.ObjectType == rhino3dm.ObjectType.Mesh and geo.IsClosed == True:
            check.append(True)
        else:
            raise ValueError('On the "room" layer, you must only have either closed brep,'
                             'or closed extrusions, closed meshes.'
                             ' Please make this change in the rhino file and try again')

    # Creating room names
    room_names = [
        geo.Attributes.Name if geo.Attributes.Name
        else "Room" + str(uuid.uuid4())[:8] for geo in volumes]

    hb_rooms = []

    # Covert solids into Ladybug Face3D objects
    for i in range(len(volumes)):
        rh_solid = volumes[i].Geometry

        if rh_solid.ObjectType == rhino3dm.ObjectType.Brep:
            lb_faces = brep3d_to_face3d(rh_solid)

        elif rh_solid.ObjectType == rhino3dm.ObjectType.Extrusion:
            lb_faces = extrusion_to_face3d(rh_solid)

        elif rh_solid.ObjectType == rhino3dm.ObjectType.Mesh:
            lb_faces = mesh_to_face3d(rh_solid)
        else:
            pass

        # Create Ladybug Polyface3D object from Ladybug Face3D objects
        lb_polyface = Polyface3D.from_faces(lb_faces, tolerance)
        name = room_names[i]

        # Create Honeybee Room object from Ladybug Polyface3D object
        hb_room = Room.from_polyface3d(name, lb_polyface)
        hb_rooms.append(hb_room)

    return hb_rooms
