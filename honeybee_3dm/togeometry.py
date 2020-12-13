"""Functions to create Ladybug Geometry objects from Rhino3dm objects."""

import warnings
import rhino3dm
import ladybug.color as lbc

from ladybug_geometry.geometry3d.pointvector import Point3D, Vector3D
from ladybug_geometry.geometry3d.face import Face3D
from ladybug_geometry.geometry3d.line import LineSegment3D
from ladybug_geometry.geometry3d.polyline import Polyline3D
from ladybug_geometry.geometry3d.mesh import Mesh3D
from ladybug_geometry.geometry3d.polyface import Polyface3D


def to_point3d(point):
    """Create a Ladybug Point3D object from a rhino3dm point.

    Args:
        point: A rhino3dm point.

    Returns:
        A Ladybug Point3D object.
    """
    return Point3D(point.X, point.Y, point.Z)


def to_vector3d(vector):
    """Create a Ladybug Vector3D from a rhino3dm Vector3d.

    Args:
        vector: A rhino3dm vector3d.

    Returns:
         A Ladybug Vector3D object.
    """
    return Vector3D(vector.X, vector.Y, vector.Z)


def remove_dup_vertices(vertices, tolerance):
    """Remove vertices from an array of Point3Ds that are equal within the tolerance.

    Args:
        vertices: A list of Ladybug Point3D objects.
        tolerance: A number for model tolerance. By default the tolerance is set to
            the ModelAbsoluteTolerance value in input 3DM file.

    Returns:
         A list of Ladybug Point3D objects with duplicate points removed.

    """
    return [pt for i, pt in enumerate(vertices)
            if not pt.is_equivalent(vertices[i - 1], tolerance)]


def check_planarity(brep, tolerance):
    """Check the planarity of a Brep.

    Args:
        brep: Geometry of a Rhino3dm Brep.

    Returns:
        Bool. True if planar. Otherwise False.
    """
    is_planar = [brep.Surfaces[i].IsPlanar(tolerance)
        for i in range(len(brep.Surfaces))]

    return all(is_planar)


def extract_mesh_faces_colors(mesh, color_by_face=False):
    """Extract face indices and colors from a Rhino mesh.

    Args:
        mesh: Rhino3dm mesh.
        color_by_face: Bool. True will derive colors from mesh faces.

    Returns:
        A tuple of mesh faces and mesh colors.
    """

    colors = None
    lb_faces = []
    for i in range(len(mesh.Faces)):
        face = mesh.Faces[i]
        if len(face) == 4:
            lb_faces.append((face[0], face[1], face[2], face[3]))
        else:
            lb_faces.append((face[0], face[1], face[2]))
    if len(mesh.VertexColors) != 0:
        colors = []
        if color_by_face is True:
            for j in range(len(mesh.Faces)):
                face = mesh.Faces[j]
                col = mesh.VertexColors[face[0]]
                colors.append(lbc.Color(col.R, col.G, col.B))
        else:
            for k in range(len(mesh.VertexColors)):
                col = mesh.VertexColors[k]
                colors.append(lbc.Color(col.R, col.G, col.B))
    return lb_faces, colors


def mesh_to_mesh3d(mesh, color_by_face=True):
    """Get a Ladybug Mesh3D object from a Rhino3dm Mesh.

    Args:
        mesh: Rhino3dm mesh.
        color_by_face: Bool. True will derive colors from mesh faces.

    Returns:
        A Ladybug Mesh3D object.
    """
    lb_verts = tuple(to_point3d(mesh.Vertices[i]) for i in range(len(mesh.Vertices)))
    lb_faces, colors = extract_mesh_faces_colors(mesh, color_by_face)
    return Mesh3D(lb_verts, lb_faces, colors)


def mesh_to_face3d(mesh):
    """Get a list of Ladybug Face3D objects from a rhino3dm Mesh.

    Args:
        mesh: A rhino3dm mesh geometry.

    Returns:
        A list of Ladybug Face3D objects.
    """

    faces = []
    try:
        pts = [to_point3d(mesh.Vertices[i]) for i in range(len(mesh.Vertices))]
    except AttributeError:
        raise AttributeError
 
    for j in range(len(mesh.Faces)):
        face = mesh.Faces[j]
        if len(face) == 4:
            all_verts = (pts[face[0]], pts[face[1]],
                         pts[face[2]], pts[face[3]])
        else:
            all_verts = (pts[face[0]], pts[face[1]], pts[face[2]])

        faces.append(Face3D(all_verts))

    return faces


def brep_to_meshed_face3d(brep, tolerance):
    """Get a Ladybug Face3D object from a planar rhino3dm Brep.

    This method meshes the brep in order to create a Ladybug
    Face3D object.

    Args:
        brep: A rhino3dm Brep.
    tolerance: A rhino3dm tolerance object. Tolerance set in the rhino file.

    Returns:
        A Ladybug Face3D object.
    """

    faces = []
    for i in range(len(brep.Faces)):
        mesh = brep.Faces[i].GetMesh(rhino3dm.MeshType.Any)
        faces.extend(mesh_to_face3d(mesh))
    try:
        polyface = Polyface3D.from_faces(faces, tolerance)
    except Exception:
        raise ValueError
    lines = list(polyface.naked_edges)
    polylines = Polyline3D.join_segments(lines, tolerance)
    face3d = Face3D(boundary=polylines[0].vertices)

    return face3d


def brep_to_mesh_to_face3d(brep):
    """Get a list of Ladybug Face3D objects from a rhino3dm Brep.

    Args:
        brep: A rhino3dm Brep.

    Returns:
        A list of Ladybug Face3D objects.
    """

    faces = []
    for i in range(len(brep.Faces)):
        mesh = brep.Faces[i].GetMesh(rhino3dm.MeshType.Any)
        faces.extend(mesh_to_face3d(mesh))
    return faces


def brep_to_face3d(brep, tolerance):
    """Get a list of Ladybug Face3D objects from a planar rhino3dm Brep.

    Args:
        brep: A rhino3dm Brep.
        tolerance: A rhino3dm tolerance object. Tolerance set in the rhino file.

    Returns:
        A list of Ladybug Face3D objects.
    """
    mesh = brep.Faces[0].GetMesh(rhino3dm.MeshType.Any)
    if not mesh:
        raise AttributeError

    # If any of the edge is an arc
    curved = False
    for i in range(len(brep.Edges)):
        if not brep.Edges[i].IsLinear(tolerance):
            curved = True
            break

    # If one of the edges is curved, mesh it
    if curved:
        return [brep_to_meshed_face3d(brep, tolerance)]

    # If the brep has 3 or 4 vertices, mesh it
    elif len(mesh.Vertices) == 4 or len(mesh.Vertices) == 3:
        return [brep_to_meshed_face3d(brep, tolerance)]

    else:
        lines = []
        # Create Ladybug lines from start and end points of edges
        for i in range(len(brep.Edges)):
            start_pt = to_point3d(brep.Edges[i].PointAtStart)
            end_pt = to_point3d(brep.Edges[i].PointAtEnd)
            line = LineSegment3D.from_end_points(start_pt, end_pt)
            lines.append(line)

        # Create Ladybug Polylines from the lines
        polylines = Polyline3D.join_segments(lines, tolerance)

        # One polyline means there are no holes
        if len(polylines) == 1:

            boundary_pts = remove_dup_vertices(polylines[0].vertices, tolerance)
            if len(boundary_pts) < 3:
                raise ValueError
            else:
                return [Face3D(boundary=boundary_pts)]

        # More than one polylines means there are holes in the brep
        elif len(polylines) > 1:

            # while creating polylines from lines if lines are remaining,
            # mesh the geometry
            check_polylines = [isinstance(polyline, Polyline3D)
                for polyline in polylines]
            if not all(check_polylines):
                try:
                    faces = brep_to_mesh_to_face3d(brep)
                except Exception:
                    raise ValueError
                else:
                    return faces

            # sort polylines based on area
            polyline_areas = [Face3D(polyline.vertices).area for polyline in polylines
                if isinstance(polyline, Polyline3D)]
            polyline_area_dict = dict(zip(polylines, polyline_areas))

            sorted_dict = sorted(polyline_area_dict.items(),
                key=lambda x: x[1], reverse=True)
            sorted_polylines = [item[0] for item in sorted_dict]

            # Points on boundary
            boundary_pts = remove_dup_vertices(
                sorted_polylines[0].vertices, tolerance)

            hole_pts = [remove_dup_vertices(polyline.vertices, tolerance)
                        for polyline in sorted_polylines[1:]]
            
            # Points on holes
            total_hole_pts = [
                pts for pts_lst in hole_pts for pts in pts_lst]
            hole_pts_on_boundary = [
                pts for pts in total_hole_pts if pts in boundary_pts]

            # If any of the hole is touching the boundary of the face, mesh it
            if len(hole_pts_on_boundary) > 0:
                warnings.warn(
                    'A Brep has holes that touch the boundary of the brep.'
                    ' This geometry will be meshed.'
                    )
                return brep_to_mesh_to_face3d(brep)
            # else create a face3d with holes
            else:
                return [Face3D(boundary=boundary_pts, holes=hole_pts)]


def brepface_to_face3d(brepFace, tolerance):
    """Get a list of Ladybug Face3D objects from a rhino3dm brepFace.

    Args:
        brepFace: A rhino3dm brepFace object.
        tolerance: A rhino3dm tolerance object. Tolerance set in the rhino file.

    Returns:
        A list of Ladybug face3d objects.
    """
    mesh = brepFace.GetMesh(rhino3dm.MeshType.Any)

    # If the brepFace is planar
    if brepFace.UnderlyingSurface().IsPlanar(tolerance):

        # Create face3ds from the brepFace, join into a Polyface and create boundary
        # polylines
        faces = mesh_to_face3d(mesh)
        try:
            polyface = Polyface3D.from_faces(faces, tolerance)
        except Exception:
            raise ValueError
        lines = list(polyface.naked_edges)
        polylines = Polyline3D.join_segments(lines, tolerance)

        # If there are no holes
        if len(polylines) == 1:
            face3d = Face3D(boundary=polylines[0].vertices)
            return [face3d]

        # If there are holes
        elif len(polylines) > 1:
            
            check_polylines = [isinstance(polyline, Polyline3D)
                for polyline in polylines]
            if not all(check_polylines):
                try:
                    faces = mesh_to_face3d(mesh)
                except Exception:
                    raise ValueError
                else:
                    return faces

            # sort polylines based on area
            polyline_areas = [Face3D(polyline.vertices).area for polyline in polylines
                if isinstance(polyline, Polyline3D)]
            polyline_area_dict = dict(zip(polylines, polyline_areas))

            sorted_dict = sorted(polyline_area_dict.items(),
                key=lambda x: x[1], reverse=True)
            sorted_polylines = [item[0] for item in sorted_dict]

            # Points on boundary
            boundary_pts = remove_dup_vertices(
                sorted_polylines[0].vertices, tolerance)

            hole_pts = [remove_dup_vertices(polyline.vertices, tolerance)
                        for polyline in sorted_polylines[1:]]

            # Points on Holes
            total_hole_pts = [
                pts for pts_lst in hole_pts for pts in pts_lst]
            hole_pts_on_boundary = [
                pts for pts in total_hole_pts if pts in boundary_pts]

            # If any hole touches the boundary, mesh it
            if len(hole_pts_on_boundary) > 0:
                warnings.warn(
                    'A Brep has holes that touch the boundary of the brep.'
                    ' This geometry will be meshed.'
                    )
                try:
                    faces = mesh_to_face3d(mesh)
                except Exception:
                    raise ValueError
                else:
                    return faces
            # else create face3d with holes
            else:
                return [Face3D(boundary=boundary_pts, holes=hole_pts)]

    else:
        try:
            faces = mesh_to_face3d(mesh)
        except Exception:
            raise ValueError
        else:
            return faces


def brep_to_brepface_to_face3d(brep, tolerance):
    """Get a  list of Ladybug Face3D objects from a Brep with multiple Brep faces.

    Args:
        brep: A rhino3dm Brep.
        tolerance: A rhino3dm tolerance object. Tolerance set in the rhino file.

    Returns:
        A list of Ladybug Face3D objects.
    """
    faces = []
    for i in range(len(brep.Faces)):
        faces.extend(brepface_to_face3d(brep.Faces[i], tolerance))
    return faces


def solid_to_face3d(brep, tolerance):
    """Get a list of Ladybug Face3D objects from a solid rhino3dm Brep.

    This function is used in translating rhino3dm solid volumes to Ladybug Face3D
    objects.

    Args:
        brep: A rhino3dm Brep.
        tolerance: A rhino3dm tolerance object. Tolerance set in the rhino file.

    Returns:
        A list of Ladybug Face3D objects.
    """
    face3ds = []

    for i in range(len(brep.Faces)):
        mesh = brep.Faces[i].GetMesh(rhino3dm.MeshType.Any)
        faces = mesh_to_face3d(mesh)
        # TODO Implement tolerance in the following statement.
        normals = set([face.normal.z for face in faces])
        if len(normals) > 1:
            # It's not a planar mesh
            face3ds.extend(faces)
        # It's a planar mesh, hence create a polyface from meshes 
        # and return a single face3d
        else:
            polyface = Polyface3D.from_faces(faces, tolerance)
            lines = list(polyface.naked_edges)
            polylines = Polyline3D.join_segments(lines, tolerance)
            face3d = Face3D(boundary=polylines[0].vertices)
            face3ds.append(face3d)

    return face3ds


def extrusion_to_face3d(extrusion, tolerance):
    """Get a list of Ladybug Face3D objects from a rhino3dm Extrusion.

    Args:
        brep: A rhino3dm Extrusion.
    tolerance: A number for tolerance value. Tolerance will only be used for
            converting mesh geometries.

    Returns:
        A list of Ladybug Face3D objects.
    """
    faces = []
    mesh = extrusion.GetMesh(rhino3dm.MeshType.Any)
    # Create face3ds
    faces = mesh_to_face3d(mesh)
    if len(faces) == 1:
        return faces
    else:
        # Group faces by normal direction
        face_normal = {face: face.normal.z for face in faces}
        face_groups = {}
        for i, v in face_normal.items():
            face_groups[v] = [i] if v not in face_groups.keys() else face_groups[v] + [i]
        for normal in face_groups:
            polyface = Polyface3D.from_faces(face_groups[normal], tolerance)
            lines = list(polyface.naked_edges)
            polylines = Polyline3D.join_segments(lines, tolerance)
            face3d = Face3D(boundary=polylines[0].vertices)
            faces.append(face3d)
        return faces


def to_face3d(obj, tolerance, *, raise_exception=False):
    """Convert Rhino objects to Ladybug Face3D objects.

    Supported object types are Brep, Extrusion and Meshes. If raise_exception is set to
    True this method will raise a ValueError for unsupported object types.

    Args:
        obj: A Rhino3dm object.
        tolerance: A number for tolerance value. Tolerance will only be used for
            converting mesh geometries.
        raise_exception: A Boolean to raise an exception for unsupported object types.
            default is False.

    Returns:
        A list of Ladybug Face3D.

    Raises:
        ValueError if object type is not supported and raise_exception is set to True.

    """
    rh_geo = obj.Geometry

    # if it's a Brep
    if isinstance(rh_geo, rhino3dm.Brep):
        # If it's a solid brep
        if rh_geo.IsSolid:
            lb_face = solid_to_face3d(rh_geo, tolerance)
        else:
            # If it's a planar brep
            if check_planarity(rh_geo, tolerance) and len(rh_geo.Faces) == 1:
                lb_face = brep_to_face3d(rh_geo, tolerance)
            # If it's not a planar brep. Such as a curved wall
            else:
                # TODO: Remove once explode brep becomes available in rhino3dm
                # lb_face = brepface_to_face3d(rh_geo, tolerance)
                lb_face = brep_to_brepface_to_face3d(rh_geo, tolerance)

    # If it's an extrusion
    elif isinstance(rh_geo, rhino3dm.Extrusion):
            lb_face = extrusion_to_face3d(rh_geo, tolerance)

    # If it's a mesh
    elif isinstance(rh_geo, rhino3dm.Mesh):
        lb_face = mesh_to_face3d(rh_geo)
        
    else:
        if raise_exception:
            raise ValueError(f'Unsupported object type: {rh_geo.ObjectType}')
        warnings.warn(
            f'Unsupported object type: {rh_geo.ObjectType} is ignored'
            )
        lb_face = []

    return lb_face
