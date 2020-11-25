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
from .helper import objects_on_parent_child, HB_layers


def import_rooms(rhino3dm_file, tolerance=None, visibility=True, config=None):
    """Import Honeybee rooms from a rhino3dm file.

    This function looks up a rhino3dm file and converts the objects
    on the layer name "room" to Honeybee Room objects.

    Args:
        rhino3dm_file: A Rhino3DM file object.
        tolerance: A number for model tolerance. By default the tolerance is set to
            the ModelAbsoluteTolerance value in input 3DM file.
        visibility: Bool. If set to False then the objects on an "off"
            layer in Rhino3dm will also be imported. Defaults to True.
        config: A dictionary. The config file as a dictionary object.
            Defaults to None.

    Returns:
        A list of Honeybee rooms.
    """
    hb_rooms = []
    config = config
    # If config file is provided and any Rhino layer is tied to HB_room layer
    if config and config['HB_layers']['HB_room']:
        solid_objs = objects_on_parent_child(rhino3dm_file,
            config['HB_layers']['HB_room'], visibility=visibility)
    
    # Take only solid objects
    solids = []
    for solid in solid_objs:
        geo = solid.Geometry
        if isinstance(geo, rhino3dm.Extrusion) and geo.IsSolid:
            solids.append(solid)
        elif isinstance(geo, rhino3dm.Brep) and geo.IsSolid:
            solids.append(solid)
        elif isinstance(geo, rhino3dm.Mesh) and geo.IsClosed:
            solids.append(solid)

    # Report if there are non-slid objects on the layer
    if len(solid_objs) != len(solids):
        diff = len(solid_objs) - len(solids)
        layer_name = config['HB_layers']['HB_room']
        warnings.warn(
            f'{diff} objects on the "{layer_name}" layer are not closed Brep or Meshes. '
            ' These objects will be ignored.'
        )
    for solid in solids:
        try:
            lb_faces = to_face3d(solid, tolerance=tolerance)
        except AttributeError:
            warnings.warn(
                'Please turn on the shaded mode in rhino, save the file, and try again.'
            )
            continue
        lb_polyface = Polyface3D.from_faces(lb_faces, tolerance)
        name = solid.Attributes.Name or clean_and_id_string('Room')
        hb_room = Room.from_polyface3d(name, lb_polyface)
        hb_rooms.append(hb_room)
  
    return hb_rooms
