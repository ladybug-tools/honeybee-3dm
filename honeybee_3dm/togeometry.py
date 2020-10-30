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

    # This is a container
    faces = []

    # If it's a Mesh
    if isinstance(geo, rhino3dm.Mesh):
        print("I am a Mesh")
        mesh = geo
        # Get all the vertices
        pts = [to_point3d(mesh.Vertices[i]) for i in range(len(mesh.Vertices))]
        for j in range(len(mesh.Faces)):
            face = mesh.Faces[j]
            if len(face) == 4:
                all_verts = (pts[face[0]], pts[face[1]],
                             pts[face[2]], pts[face[3]])
            else:
                all_verts = (pts[face[0]], pts[face[1]], pts[face[2]])
            # Create Ladybug Face3D objects based on tuples of vertices
            faces.append(Face3D(all_verts))

    # If it's an Extrusion
    if isinstance(geo, rhino3dm.Extrusion):
        print("I am an Extrusion")
        # Convert it into a Mesh first
        mesh = geo.GetMesh(rhino3dm.MeshType.Default)
        if isinstance(mesh, rhino3dm.Mesh):
            # Get all the vertices
            pts = [to_point3d(mesh.Vertices[i])
                   for i in range(len(mesh.Vertices))]
            for j in range(len(mesh.Faces)):
                face = mesh.Faces[j]
                if len(face) == 4:
                    all_verts = (pts[face[0]], pts[face[1]],
                                 pts[face[2]], pts[face[3]])
                else:
                    all_verts = (pts[face[0]], pts[face[1]], pts[face[2]])
                # Create Ladybug Face3D objects based on tuples of vertices
                faces.append(Face3D(all_verts))

    # If it's a Brep
    if isinstance(geo, rhino3dm.Brep):
        print("I am a Brep")
        # Convert it into a list of Meshes
        meshes = [geo.Faces[f].GetMesh(rhino3dm.MeshType.Any) for f in range(
            len(geo.Faces)) if type(geo.Faces[f]) != list]

        # For each Mesh in the list create a Ladybug Face3D object and add to
        # a container
        for i in range(len(meshes)):
            if isinstance(meshes[i], rhino3dm.Mesh):
                mesh = meshes[i]
                # Get all the vertices
                pts = [to_point3d(mesh.Vertices[i])
                       for i in range(len(mesh.Vertices))]
                for j in range(len(mesh.Faces)):
                    face = mesh.Faces[j]
                    if len(face) == 4:
                        all_verts = (pts[face[0]], pts[face[1]],
                                     pts[face[2]], pts[face[3]])
                    else:
                        all_verts = (pts[face[0]], pts[face[1]], pts[face[2]])
                    # Create Ladybug Face3D objects based on tuples of vertices
                    faces.append(Face3D(all_verts))

    return faces
