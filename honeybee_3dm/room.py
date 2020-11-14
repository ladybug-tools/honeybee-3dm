"""Creating Honeybee Room objects from rhino3dm closed volumes"""

# The Rhino3dm library provides the ability to access content of a Rhino3dm
# file from outside of Rhino
import rhino3dm

import warnings

# Importing core Honeybee & Ladybug Geometry dependencies
from honeybee.room import Room
from honeybee.typing import clean_and_id_string
from ladybug_geometry.geometry3d.polyface import Polyface3D

# Importing dependencies from Honeybee-3dm package
from .togeometry import to_face3d
from .helper import filter_objects_by_layer


def import_rooms(rhino3dm_file, tolerance=None):
    """Import Honeybee rooms from a rhino3dm file.

    This function looks up a rhino3dm file and converts the objects
    on the layer name "room" to Honeybee Room objects.

    Args:
        rhino3dm_file: A Rhino3DM file object.
        tolerance: A number for model tolerance. By default the tolerance is set to
            the ModelAbsoluteTolerance value in input 3DM file.

    Returns:
        A list of Honeybee rooms.
    """
    # rooms from rhino file
    try:
        volumes = filter_objects_by_layer(rhino3dm_file, 'room')
    except ValueError:
        # no layer named room
        return []

    # From all the objects on the layer named "room" take only solid objects
    closed_volumes = []
    for vol in volumes:
        geo = vol.Geometry
        if isinstance(geo, rhino3dm.Extrusion) and geo.IsSolid:
            closed_volumes.append(vol)
        elif isinstance(geo, rhino3dm.Brep) and geo.IsSolid:
            closed_volumes.append(vol)
        elif isinstance(geo, rhino3dm.Mesh) and geo.IsClosed:
            closed_volumes.append(vol)

    if len(closed_volumes) != len(volumes):
        diff = len(volumes) - len(closed_volumes)
        warnings.warn(
            f'{diff} objects on the "room" layer are not closed Brep or Meshes. '
            ' These objects will be ignored.'
        )

    hb_rooms = []
    # Covert solids into Ladybug Face3D objects
    for volume in closed_volumes:
        lb_faces = to_face3d(volume, tolerance=tolerance)
        # Create Ladybug Polyface3D object from Ladybug Face3D objects
        lb_polyface = Polyface3D.from_faces(lb_faces, tolerance)
        # Assign name
        name = volume.Attributes.Name or clean_and_id_string('Room')
        # Create Honeybee Room object from Ladybug Polyface3D object
        hb_room = Room.from_polyface3d(name, lb_polyface)
        hb_rooms.append(hb_room)

    return hb_rooms
