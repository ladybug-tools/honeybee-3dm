"""Functions to create Ladybug geometries from Rhino3dm geometries."""

# The Rhino3dm library provides the ability to access content of a Rhino3dm
# file from outside of Rhino
import rhino3dm

# Importing Ladybug geometry dependencies
from ladybug_geometry.geometry3d.pointvector import Point3D, Vector3D
from ladybug_geometry.geometry3d.face import Face3D
from ladybug_geometry.geometry3d.line import LineSegment3D
from ladybug_geometry.geometry3d.polyline import Polyline3D


def to_point3d(point):
    """Ladybug Point3D from a rhino3dm point."""
    return Point3D(point.X, point.Y, point.Z)


def to_vector3d(vector):
    """Ladybug Vector3D from a rhino3dm Vector3d."""
    return Vector3D(vector.X, vector.Y, vector.Z)


def remove_dup_verts(vertices):
    """Remove vertices from an array of Point3Ds that are equal within the tolerance."""
    return [pt for i, pt in enumerate(vertices)
            if not pt.is_equivalent(vertices[i - 1], 0.001)]


def mesh_to_face3d(mesh):
    """list of Ladybug Face3D from a rhino3dm Mesh."""
    faces = []
    pts = [to_point3d(mesh.Vertices[i]) for i in range(len(mesh.Vertices))]

    for j in range(len(mesh.Faces)):
        face = mesh.Faces[j]
        if len(face) == 4:
            all_verts = (pts[face[0]], pts[face[1]],
                         pts[face[2]], pts[face[3]])
        else:
            all_verts = (pts[face[0]], pts[face[1]], pts[face[2]])

        faces.append(Face3D(all_verts))

    return faces


def brep_to_face3d(brep):
    """list of Ladybug Face3D from a rhino3dm Brep."""
    faces = []
    for i in range(len(brep.Faces)):
        mesh = brep.Faces[i].GetMesh(rhino3dm.MeshType.Any)
        faces.extend(mesh_to_face3d(mesh))

    return faces


def brep2d_to_face3d(brep, tolerance):
    """list of Ladybug Face3D from a planar rhino3dm Brep."""
    faces = []
    try:
        # Check 01 - If any of the edge is an arc
        lines = []
        not_line = 0
        for i in range(len(brep.Edges)):
            if brep.Edges[i].IsLinear(tolerance) == False:
                not_line += 1
        # If there's an arc in one of the edges, mesh it
        if not_line > 0:
            print("The surface has curved edges. It will be meshed")
            faces.extend(brep_to_face3d(brep))
        else:
            # Create Ladybug lines from start and end points of edges
            for i in range(len(brep.Edges)):
                start_pt = to_point3d(brep.Edges[i].PointAtStart)
                end_pt = to_point3d(brep.Edges[i].PointAtEnd)
                line = LineSegment3D.from_end_points(start_pt, end_pt)
                lines.append(line)

            # Create Ladybug Polylines from the lines
            polylines = Polyline3D.join_segments(lines, tolerance)
            # Sort the Ladybug Polylines based on length
            # The longest polyline belongs to the boundary of the face
            # The rest of the polylines belong to the holes in the face
            sorted_polylines = sorted(
                polylines, key=lambda polyline: polyline.length)
            # The first polyline in the list shall always be the polyline for
            # the boundary
            sorted_polylines.reverse()

            # Getting all vertices of the face
            mesh = brep.Faces[0].GetMesh(rhino3dm.MeshType.Any)
            mesh_pts = [to_point3d(mesh.Vertices[i])
                        for i in range(len(mesh.Vertices))]

            # In the list of the Polylines, if there's only one polyline then
            # the face has no holes
            if len(sorted_polylines) == 1:
                if len(mesh_pts) == 4 or len(mesh_pts) == 3:
                    faces.extend(mesh_to_face3d(mesh))
                else:
                    boundary_pts = remove_dup_verts(
                        sorted_polylines[0].vertices)
                    lb_face = Face3D(boundary=boundary_pts)
                    faces.append(lb_face)

            # In the list of the Polylines, if there's more than one polyline then
            # the face has hole / holes
            elif len(sorted_polylines) > 1:
                boundary_pts = remove_dup_verts(sorted_polylines[0].vertices)
                hole_pts = [remove_dup_verts(polyline.vertices)
                            for polyline in sorted_polylines[1:]]
                # Merging lists of hole_pts
                total_hole_pts = [
                    pts for pts_lst in hole_pts for pts in pts_lst]
                hole_pts_on_boundary = [
                    pts for pts in total_hole_pts if pts in boundary_pts]
                # Check 02 - If any of the hole is touching the boundary of the face
                # then mesh it
                if len(hole_pts_on_boundary) > 0:
                    print(
                        "The surface has holes that touch the boundary. \
                            It will be meshed")
                    faces.extend(brep_to_face3d(brep))
                else:
                    lb_face = Face3D(boundary=boundary_pts, holes=hole_pts)
                    faces.append(lb_face)
    # If any of the above fails, mesh it
    except Exception as e:
        print(str(e) + "Face creation failed, this face will be meshed")
        faces.extend(brep_to_face3d(brep))

    return faces


def brep3d_to_face3d(brep):
    """list of Ladybug Face3D from a solid rhino3dm Brep."""
    faces = []
    for i in range(len(brep.Faces)):
        mesh = brep.Faces[i].GetMesh(rhino3dm.MeshType.Any)
        faces.extend(mesh_to_face3d(mesh))

    return faces


def extrusion_to_face3d(extrusion):
    """list of Ladybug Face3D from a rhino3dm Extrusion."""
    faces = []
    mesh = extrusion.GetMesh(rhino3dm.MeshType.Any)
    faces.extend(mesh_to_face3d(mesh))

    return faces
