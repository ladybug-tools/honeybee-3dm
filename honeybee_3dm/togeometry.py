"""Functions to create Ladybug geometries from Rhino3dm geometries."""

import rhino3dm
from ladybug_geometry.geometry3d.pointvector import Point3D
from ladybug_geometry.geometry3d.face import Face3D
from ladybug_geometry.geometry3d.plane import Plane
from ladybug_geometry.geometry3d.pointvector import Point3D, Vector3D


def to_point3d(point):
    """Ladybug point3D from a rhino3dm point.

    Args:
        point (point3d): A rhino3dm point
    """
    return Point3D(point.X, point.Y, point.Z)


def to_vector3d(vector):
    """Ladybug Vector3D from Rhino Vector3d."""
    return Vector3D(vector.X, vector.Y, vector.Z)


def to_face3d(geo, meshing_parameters=None):
    """This method converts a rhino face into a Ladybug Face3D object. The
    Face3D object is one of the foundational objects in honeybee.

    Args:
        geo (A Rhino Brep, Surface or Mesh): This will be converted into a list
        of Ladybug Face3D.
        meshing_parameters (string): Optional Rhino Meshing Parameters
        to describe how curved faces should be converted into planar elements.
        If None, Rhino3dm's Default Meshing Parameters will be used.
    """

    faces = []  # converted list of faces will be stored here.

    # If it's a mesh, get all the vertices
    if isinstance(geo, rhino3dm.Mesh):
        pts = [to_point3d(geo.Vertices[i]) for i in range(len(geo.Vertices))]
        faces.append(Face3D(pts))

    # If it's a Rhino Surface, Rhino trimmed surface or rhino open polysurface
    # Convert into mesh and get all the vertices
    elif isinstance(geo, rhino3dm.Brep):

        mesh_type = rhino3dm.MeshType.Default
        # geo = geo.Faces[0].GetMesh(mesh_type)
        # point = geo.Vertices[0]                          # For plane creation
        # point3d = to_point3d(point)                      # For plane creation
        # vectors = geo.Normals  # For plane creation
        # pts = [to_point3d(geo.Vertices[i]) for i in range(len(geo.Vertices))]
        # vector = vectors[0]                              # For plane creation
        # vector3d = to_vector3d(vector)                   # For plane creation
        # plane = Plane(vector3d, point3d)                 # For plane creation
        # faces.append(Face3D(pts, plane))
        for i in range(len(geo.Faces)):
            face = geo.Faces[i].GetMesh(mesh_type)
            pts = [to_point3d(face.Vertices[j])
                   for j in range(len(face.Vertices))]
            print(pts)
            faces.append(Face3D(pts))

        # If it's rhino extrusion, convert into mesh and get all vertices
    elif isinstance(geo, rhino3dm.Extrusion):
        mesh_type = rhino3dm.MeshType.Default
        geo = geo.GetMesh(mesh_type)
        pts = [to_point3d(geo.Vertices[i]) for i in range(len(geo.Vertices))]
        faces.append(Face3D(pts))

    return faces
