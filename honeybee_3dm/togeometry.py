"""Functions to create Ladybug geometries from Rhino3dm geometries."""

# The Rhino3dm library provides the ability to access content of a Rhino3dm
# file from outside of Rhino
import rhino3dm

# Importing Ladybug geometry libraries
# The Ladybug geometry objects are foundation to other objects in Ladybug and Honeybee
from ladybug_geometry.geometry3d.pointvector import Point3D, Vector3D
from ladybug_geometry.geometry3d.face import Face3D


def to_point3d(point):
    """This function creates a Ladybug Point3D object from a rhino3dm point.

    Args:
        point (point3d): A rhino3dm point

    Returns:
        Point3D: A Ladybug Point3D object
    """
    return Point3D(point.X, point.Y, point.Z)


def to_vector3d(vector):
    """This function creates a Ladybug Vector3D from a rhino3dm Vector3d.

    Args:
        vector (vector3d): A rhino3dm vector3d

    Returns:
         Vector3D: A Ladybug Vector3D object
    """
    return Vector3D(vector.X, vector.Y, vector.Z)


def mesh_to_face3d(mesh):
    """This function creates a Ladybug Face3D object out of a rhino3dm Mesh.

    Args:
        mesh (mesh): A rhino3dm mesh geometry

    Returns:
        A list: A list of Ladybug Face3D objects
    """
    # Ladybug Face3D objects will be collected here
    faces = []

    # Get vertices of the rhino3dm mesh
    vertices = mesh.Vertices
    pts = [to_point3d(vertices[i]) for i in range(len(vertices))]

    # For each mesh face create a tuple of vertices
    for j in range(len(mesh.Faces)):
        face = mesh.Faces[j]
        if len(face) == 4:
            all_verts = (pts[face[0]], pts[face[1]],
                         pts[face[2]], pts[face[3]])
        else:
            all_verts = (pts[face[0]], pts[face[1]], pts[face[2]])

        # Create a Ladybug Face3D object based on tuples of vertices
        faces.append(Face3D(all_verts))

    return faces


def brep_to_face3d(brep):
    """This function creates a Ladybug Face3D object from a rhino3dm Brep

    Args:
        brep (Brep): A rhino3dm Brep

    Returns:
        A list : A list of Ladybug Face3D objects
    """
    # Ladybug Face3D objects will be collected here
    faces = []
    # Get all the Brep faces
    for i in range(len(brep.Faces)):
        # Convert Brep faces into Meshes
        mesh = brep.Faces[i].GetMesh(rhino3dm.MeshType.Any)
        faces.extend(mesh_to_face3d(mesh))
    return faces


def extrusion_to_face3d(extrusion):
    """This function creates a Ladybug Face3D object from a rhino3dm Extrusion

    Args:
        brep (Extrusion): A rhino3dm Extrusion

    Returns:
        A list : A list of Ladybug Face3D objects
    """
    # Ladybug Face3D objects will be collected here
    faces = []
    # Convert the Extrusion into Mesh
    mesh = extrusion.GetMesh(rhino3dm.MeshType.Any)
    faces.extend(mesh_to_face3d(mesh))
    return faces
