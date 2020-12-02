"""Create Honeybee objects(Face, Shade, Aperture, Door, Grid) from planar geometries
in a Rhino 3DM file."""

from honeybee.face import Face
from honeybee.typing import clean_and_id_string, clean_string

from .togeometry import to_face3d
from .layer import objects_on_layer, objects_on_parent_child
from .grid import import_grids
from .config import grid_controls, face3d_to_face_type_to_hb_face, face3d_to_hb_object
from .config import face3d_to_rad_to_hb_face, child_layer_control


def import_objects_with_config(rhino3dm_file, layer, *, tolerance=None, visibility=True,
    config=None, modifiers_dict=None):
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
        config: A dictionary of config settings. Defaults to None
        modifiers_dict: A dictionary with radiance identifier to modifier structure.
            Defaults to None.

    Returns:
        A tuple of following lists;
        Honeybee Face objects,
        Honeybee Shade objects,
        Honeybee Aperture objects,
        Honeybee Door objects,
        Honeybee grids
        A list wil be empty if no objects are imported from rhino file.

    """
    # Placeholders
    hb_faces, hb_shades, hb_apertures, hb_doors, hb_grids = tuple([[] for _ in range(5)])

    # If Grids are requested for a layer
    if grid_controls(config, layer.Name):

        hb_grids = import_grids(rhino3dm_file, layer,
            grid_controls=grid_controls(config, layer.Name),
            child_layer=child_layer_control(config, layer.Name), tolerance=tolerance)

    # If Grids are not requested for a layer
    else:
        # If child layers needs to be included
        if child_layer_control(config, layer.Name):
            objects = objects_on_parent_child(rhino3dm_file, layer.Name,
                visibility=visibility)

        # If child layers do not need to be included
        else:
            objects = objects_on_layer(rhino3dm_file, layer, visibility=visibility)
    
        for obj in objects:
            try:
                lb_faces = to_face3d(obj, tolerance=tolerance)
            except AttributeError:
                raise AttributeError(
                    'Please turn on the shaded mode in rhino, save the file,'
                    ' and try again.'
                )
            name = obj.Attributes.Name

            for face_obj in lb_faces:
                # If face_type settting is employed
                if 'honeybee_face_type' in config['layers'][layer.Name]:
                    hb_faces.append(face3d_to_face_type_to_hb_face(config, face_obj,
                        name, layer.Name))
                
                # If only radiance material settting is employed
                elif 'honeybee_face_type' not in config['layers'][layer.Name] and\
                    'honeybee_face_object' not in config['layers'][layer.Name] and\
                        'radiance_material' in config['layers'][layer.Name]:
                    hb_faces.append(face3d_to_rad_to_hb_face(config, face_obj, name,
                        layer.Name))
                
                # If face_object settting is employed
                elif 'honeybee_face_object' in config['layers'][layer.Name]:
                    hb_objects = face3d_to_hb_object(config, face_obj, name,
                        layer.Name)
                    hb_apertures.extend(hb_objects[0])
                    hb_shades.extend(hb_objects[1])
                    hb_doors.extend(hb_objects[2])

    return hb_faces, hb_shades, hb_apertures, hb_doors, hb_grids


def import_objects(file_3dm, layer, *, tolerance=None, visibility=True):
    """Get default Honeybee Faces for a Rhino3dm layer.

    Args:
        file_3dm: A Rhino3dm file object.
        layer: A Rhino3dm layer object.
        tolerance: A number for model tolerance. By default the tolerance is set to
            the ModelAbsoluteTolerance value in input 3DM file. Defaults to None.
        visibility: Bool. If set to False then the objects on an "off"
            layer and hidden objects in Rhino3dm will also be imported.
            Defaults to True.

    Returns:
        A list of Honeybee Face objects.
    """
    hb_faces = []
    objects = objects_on_layer(file_3dm, layer=layer, visibility=visibility)
    
    for obj in objects:
        try:
            lb_faces = to_face3d(obj, tolerance=tolerance)
        except AttributeError:
            raise AttributeError(
                'Please turn on the shaded mode in rhino, save the file,'
                ' and try again.'
            )

        name = obj.Attributes.Name

        for face_obj in lb_faces:
            obj_name = name or clean_and_id_string(layer.Name)
            args = [clean_string(obj_name), face_obj]
            hb_face = Face(*args)
            hb_face.display_name = args[0]
            hb_faces.append(hb_face)

    return hb_faces
    