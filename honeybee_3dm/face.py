"""Creating Honeybee face objects(Face, Shade, Aperture, Door) from rhino3dm
planar geometries"""

# The Rhino3dm library provides the ability to access content of a Rhino3dm
# file from outside of Rhino
import rhino3dm

# The uuid library is used to create names for Honeybee object when a name
# is not assigned by a user
import uuid

# Importing core Honeybee & Ladybug Geometry dependencies
from honeybee.face import Face
from honeybee.shade import Shade
from honeybee.aperture import Aperture
from honeybee.door import Door
from honeybee.facetype import face_types
from honeybee.boundarycondition import boundary_conditions
from honeybee.typing import clean_and_id_string
from honeybee.facetype import face_types
from ladybug_geometry.geometry3d.face import Face3D

# Importing dependencies from Honeybee-3dm package
from .togeometry import extrusion_to_face3d, mesh_to_face3d, brep2d_to_face3d, brep3d_to_face3d


def to_face(rhino3dm_file, tolerance):
    """Creates Honeybee faces from a rhino3dm file.

    This function looks up a rhino3dm file, converts the objects
    on the layer name "roof", "wall", "floor", "airwall", "shade", and  "aperture"
    to Honeybee objects, and writes them to a json file.

    Args:
        rhino3dm_file: The rhino file from which Honeybee faces will be created.
        tolerance: A rhino3dm tolerance object. Tolerance set in the rhino file.

    Returns:
        A list of Honeybee faces.
    """
    hb_faces = []

    layer_dict = {
        layer.Name: layer.Index for layer in rhino3dm_file.Layers}

    # A Layer dictionary with layer name : (Honeybee face_type, Class) structure
    layer_to_hb_object = {
        'roof': (face_types.roof_ceiling, Face),
        'wall': (face_types.wall, Face),
        'floor': (face_types.floor, Face),
        'airwall': (face_types.air_boundary, Face),
        'shade': (None, Shade),
        'aperture': (None, Aperture),
        'door': (None, Door)}

    for layer in layer_to_hb_object:

        if layer in layer_dict:
            hb_face_type, hb_face_module = layer_to_hb_object[layer]

            # Gathering planar geometries from the layer
            rhino_faces = [obj for obj in rhino3dm_file.Objects
                           if obj.Attributes.LayerIndex == layer_dict[layer]]

            # Creating face names
            face_names = [geo.Attributes.Name if geo.Attributes.Name else layer +
                          str(uuid.uuid4())[:8] for geo in rhino_faces]

            # for each rhino geometry gathered, Converting the Rhino3dm geometry
            # into a Ladybug Face3D objects
            for count, face in enumerate(rhino_faces):
                rh_face = face.Geometry

                if rh_face.ObjectType == rhino3dm.ObjectType.Brep:
                    if rh_face.IsSolid == True:
                        lb_face = brep3d_to_face3d(rh_face)
                    elif rh_face.IsSolid == False:
                        lb_face = brep2d_to_face3d(rh_face, tolerance)

                elif rh_face.ObjectType == rhino3dm.ObjectType.Extrusion:
                    lb_face = extrusion_to_face3d(rh_face)

                elif rh_face.ObjectType == rhino3dm.ObjectType.Mesh:
                    lb_face = mesh_to_face3d(rh_face)
                else:
                    pass

                # Converting Ladybug Face3D into Honeybee Objects
                for face_obj in lb_face:

                    if hb_face_module == Face:
                        hb_face = hb_face_module(clean_and_id_string('{}'.format(
                            face_names[count])), face_obj, hb_face_type)

                    elif hb_face_module == Shade or hb_face_module == Aperture \
                            or hb_face_module == Door:
                        hb_face = hb_face_module(clean_and_id_string(
                            '{}'.format(face_names[count])), face_obj)

                    # Assigning a name to the Honeybee Face
                    hb_face.display_name = '{}'.format(
                        face_names[count])
                    hb_faces.append(hb_face)
        else:
            pass

    return hb_faces
