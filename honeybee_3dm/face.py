"""Create Honeybee face objects(Face, Shade, Aperture, Door) from planar geometries
in a Rhino 3DM file."""

# Importing core Honeybee & Ladybug Geometry dependencies
from honeybee.face import Face
from honeybee.shade import Shade
from honeybee.aperture import Aperture
from honeybee.door import Door
from honeybee.facetype import face_types
from honeybee.typing import clean_and_id_string, clean_string

# Importing dependencies from Honeybee-3dm package
from .togeometry import to_face3d
from .helper import HB_layers, filter_objects_by_layer, parent_child_index


def import_faces(rhino3dm_file, tolerance=None, visibility=True, config=None):
    """Import Rhino planar geometry as Honeybee faces.

    This function looks up a rhino3dm file, converts the objects
    on the layer name "roof", "wall", "floor", "airwall", "shade", and  "aperture"
    to Honeybee objects, and converts them to Honeybee faces.

    Args:
        rhino3dm_file: A Rhino3DM file object.
        tolerance: A number for model tolerance. By default the tolerance is set to
            the ModelAbsoluteTolerance value in input 3DM file.
        visibility: Bool. If set to False then the objects on an "off"
            layer in Rhino3dm will also be imported. Defaults to True.
        config: A dictionary. The config file as a dictionary object.
            Defaults to None.
    Returns:
        A list of Honeybee faces.

    """
    hb_faces = []
    hb_shades = []
    hb_apertures = []
    hb_doors = []
    config = config
    # If config file is provided and any Rhino layer is assigned
    if config and config['HB_layers'].values():
        # Map rhino layers to HB_layers based on the config file
        hb_layer_from_layer = {config['HB_layers'][key]: key for key in 
            config['HB_layers']}
        # A Layer dictionary with HB_layer : (Honeybee face_type, Class) structure
        layer_to_hb_object = {
            HB_layers.roof.value: (face_types.roof_ceiling, Face),
            HB_layers.wall.value: (face_types.wall, Face),
            HB_layers.floor.value: (face_types.floor, Face),
            HB_layers.airwall.value: (face_types.air_boundary, Face),
            HB_layers.shade.value: (None, Shade),
            HB_layers.aperture.value: (None, Aperture),
            HB_layers.door.value: (None, Door)
        }

    for layer in rhino3dm_file.Layers:
        # If the rhino layer is tied to a HB_layer in the config file and it is not
        # tied to HB layers for Grids, Rooms, and Views
        if layer.Name in config['HB_layers'].values() \
            and layer.Name != config['HB_layers']['HB_grid'] \
            and layer.Name != config['HB_layers']['HB_room'] \
            and layer.Name != config['HB_layers']['HB_view']:
            # Get face type and Honeybee Module
            hb_face_type, hb_face_module = layer_to_hb_object[
                    hb_layer_from_layer[layer.Name]]
            # Get objects on the rhino layer and its child layers
            objects = filter_objects_by_layer(rhino3dm_file, layer.Name, 
                visibility=visibility)
            for obj in objects:
                lb_faces = to_face3d(obj, tolerance=tolerance)
                name = obj.Attributes.Name
                for face_obj in lb_faces:
                    # Assign a name to the object
                    obj_name = name or clean_and_id_string(layer.Name)
                    args = [clean_string(obj_name), face_obj]
                    # If there's a face type the object is either of the
                    # Wall, Floor, Roof, Ceiling, Airwall
                    if hb_face_type:
                        args.append(hb_face_type)
                        hb_face = hb_face_module(*args)
                        hb_face.display_name = args[0]
                        hb_faces.append(hb_face)
                    # If there's no face type then assign Honeybee module based on
                    # rhino layer name
                    else:
                        # Honeybee Shade object
                        if hb_layer_from_layer[layer.Name] == HB_layers.shade.value:
                            hb_shade = hb_face_module(*args)
                            hb_shade.display_name = args[0]
                            hb_shades.append(hb_shade)
                        # Honeybee Shade object
                        elif hb_layer_from_layer[layer.Name] == HB_layers.aperture.value:
                            hb_aperture = hb_face_module(*args)
                            hb_aperture.display_name = args[0]
                            hb_apertures.append(hb_aperture)
                        # Honeybee Shade object
                        elif hb_layer_from_layer[layer.Name] == HB_layers.door.value:
                            hb_door = hb_face_module(*args)
                            hb_door.display_name = args[0]
                            hb_doors.append(hb_door)

        # If the rhino layer is not tied to a HB_layer in the config file and it is not
        # tied to HB layers for Grids, Rooms, and Views
        # Assign Honeybee Faces based on normal direction of Rhino face
        else: 
            if layer.Name != config['HB_layers']['HB_grid'] \
                and layer.Name != config['HB_layers']['HB_room'] \
                and layer.Name != config['HB_layers']['HB_view']:

                parent_layer = parent_child_index(rhino3dm_file, rhino3dm_file.Layers)
                print(parent_layer)
 
                # Get objects on the rhino layer and its child layers
                objects = filter_objects_by_layer(rhino3dm_file, layer.Name, 
                    visibility=visibility)
                for obj in objects:
                    lb_faces = to_face3d(obj, tolerance=tolerance)
                    name = obj.Attributes.Name
                    for face_obj in lb_faces:
                        obj_name = name or clean_and_id_string(layer.Name)
                        args = [clean_string(obj_name), face_obj]
                        hb_face = Face(*args)
                        hb_face.display_name = args[0]
                        hb_faces.append(hb_face)

    return hb_faces, hb_shades, hb_apertures, hb_doors
