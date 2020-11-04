"""Creating Honeybee face objects(Face, Shade, Aperture, Door) from rhino3dm
planar geometries"""

# The Rhino3dm library provides the ability to access content of a Rhino3dm
# file from outside of Rhino
import rhino3dm
import uuid

# Importing dependencies from Honeybee-3dm package
from .togeometry import brep_to_face3d, extrusion_to_face3d, mesh_to_face3d
from .tojson import to_json

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


def to_face(path):
    """This function looks up a rhino3dm file, converts the objects
    on the layer name "roof", "wall", "floor", "airwall", "shade", and  "aperture"
    to Honeybee objects, and writes them to a json file.

    Args:
        path (A string): The path to the rhino file
    """
    # TODO create a quality check for the file path

    # Creating a rhino3dm object from the file at the path provided
    rhino3dm_file = rhino3dm.File3dm.Read(path)
    tolerance = rhino3dm_file.Settings.ModelAbsoluteTolerance

    #  All the Honeybee objects will be collected here
    hb_faces = []

    # A dictionary with layer name : layer index structure
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

    # For each layer in the dictionary
    for layer in layer_to_hb_object.keys():
        # If the layer is also in the rhino3dm file
        if layer in layer_dict.keys():
            hb_face_type, hb_face_module = layer_to_hb_object[layer]

            # Gathering planar geometries from the layer
            rhino_faces = [object for object in rhino3dm_file.Objects
                           if object.Attributes.LayerIndex == layer_dict[layer]]

            # Creating face names
            face_names = [geo.Attributes.Name if geo.Attributes.Name else layer +
                          str(uuid.uuid4())[:8] for geo in rhino_faces]

            # for each rhino geometry gathered, Converting the Rhino3dm geometry
            # into a Ladybug Face3D objects
            for count, face in enumerate(rhino_faces):
                rh_face = face.Geometry
                # If it's a Brep, create Ladybug Face3D objects from it
                if rh_face.ObjectType == rhino3dm.ObjectType.Brep:
                    lb_face = brep_to_face3d(rh_face)
                # If it's an Extrusion, create Ladybug Face3D objects from it
                elif rh_face.ObjectType == rhino3dm.ObjectType.Extrusion:
                    lb_face = extrusion_to_face3d(rh_face)
                # If it's a Mesh, create Ladybug Face3D objects from it
                elif rh_face.ObjectType == rhino3dm.ObjectType.Mesh:
                    lb_face = mesh_to_face3d(rh_face)
                else:
                    print(
                        f'There are objects on layer "{layer}" that this library does not support.')

                # Converting Ladybug Face3D into Honeybee Objects
                for face_obj in lb_face:
                    # If the object is on a layer named "wall", "roof", "floor", or "airwall"
                    if hb_face_module == Face:
                        hb_face = hb_face_module(clean_and_id_string('{}_{}'.format(
                            face_names[count], count)), face_obj, hb_face_type)
                    # If the objects is on a layer named "shade"
                    elif hb_face_module == Shade:
                        hb_face = hb_face_module(clean_and_id_string(
                            '{}_{}'.format(face_names[count], count)), face_obj)
                    # If the objects is on a layer named "aperture"
                    elif hb_face_module == Aperture:
                        hb_face = hb_face_module(clean_and_id_string(
                            '{}_{}'.format(face_names[count], count)), face_obj)
                    # If the objects is on a layer named "Door"
                    elif hb_face_module == Door:
                        hb_face = hb_face_module(clean_and_id_string(
                            '{}_{}'.format(face_names[count], count)), face_obj)
                    else:
                        pass

                    # Assigning a name to the Honeybee Face
                    hb_face.display_name = '{}_{}'.format(
                        face_names[count], count)
                    hb_faces.append(hb_face)
        else:
            print(f'Layer "{layer}" is not supported by this library')

    return hb_faces
