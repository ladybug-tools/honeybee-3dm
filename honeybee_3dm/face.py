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


def layer_name_to_hb_objects(layer):
    """This function takes a Rhino layer and spits out a Honeybee face type
    and Honeybee Class to be used for Rhino to Honeybee translation.

    Args:
        layer (A string): Name of the rhino3dm layer

    Returns:
        hb_type: A Honeybee face type object
        hb_face_module: A Honeybee class. It is either of Face, Shade, Aperture, or Door
    """
    hb_type = " "  # Variable holding a Honeybee face type
    hb_face_module = " "  # Variable holding a Honeybee module name

    if layer == "roof":
        hb_type = face_types.roof_ceiling
        hb_face_module = Face
    elif layer == "wall":
        hb_type = face_types.wall
        hb_face_module = Face
    elif layer == "floor":
        hb_type = face_types.floor
        hb_face_module = Face
    elif layer == "airwall":
        hb_type = face_types.air_boundary
        hb_face_module = Face
    elif layer == "shade":
        hb_type = None
        hb_face_module = Shade
    elif layer == "aperture":
        hb_type = None
        hb_face_module = Aperture
    elif layer == "door":
        hb_type = None
        hb_face_module = Door
    elif layer == "Default":
        pass

    return (hb_type, hb_face_module)


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

    # Gathering layer information from the rhino file
    layers = rhino3dm_file.Layers
    layer_names = [layer_name.Name for layer_name in layers]
    layer_indexes = [layer_name.Index for layer_name in layers]
    layer_dict = dict(zip(layer_names, layer_indexes))

    # For each layer in the rhino3dm file
    for layer in layer_names:
        # Select Honeybee Face type
        hb_face_type = layer_name_to_hb_objects(layer)[0]
        # Select Honeybee Class
        hb_face_module = layer_name_to_hb_objects(layer)[1]
        # Layer name
        layer_name = layer

        # Gathering planar geometries from the layer
        rhino_faces = [object for object in rhino3dm_file.Objects if object.Attributes.LayerIndex ==
                       layer_dict[layer_name]]

        # Creating face names
        face_names = []
        for count, geo in enumerate(rhino_faces):
            # If there's a user defined name of the object in rhino3dm, use it
            if len(geo.Attributes.Name) > 0:
                face_names.append(geo.Attributes.Name)
            # Else, generate a unique name
            else:
                name = layer_name + str(uuid.uuid4())[:8]
                face_names.append(name)

        # for each rhino geometry gathered, Converting the Rhino3dm geometry
        # into a Ladybug Face3D objects
        for i in range(len(rhino_faces)):
            rh_face = rhino_faces[i].Geometry
            # If it's a Brep, create Ladybug Face3D objects from it
            if rh_face.ObjectType == rhino3dm.ObjectType.Brep:
                lb_face = brep_to_face3d(rh_face)
            # If it's an Extrusion, create Ladybug Face3D objects from it
            if rh_face.ObjectType == rhino3dm.ObjectType.Extrusion:
                lb_face = extrusion_to_face3d(rh_face)
            # If it's a Mesh, create Ladybug Face3D objects from it
            if rh_face.ObjectType == rhino3dm.ObjectType.Mesh:
                lb_face = mesh_to_face3d(rh_face)

            # Converting Ladybug Face3D into Honeybee Face
            for j in range(len(lb_face)):
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

    return hb_faces
