"""Functions to create Ladybug Geometry objects from Rhino3dm objects."""
# In this module, you will observe that instead of using the pythonic way of
# iterating through a list, iterators(studs such as "i" and "j") are used. 
# This is deliberate and it is done to bypass the wrong number of 
# items extracted from a list when accesses throug the pythonic way.

import warnings
import rhino3dm
import ladybug.color as lbc
from math import isclose

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
        Bool. True if planar otherwise False.
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
    """Get a Ladybug Face3D object from a planar rhino3dm Brep.

    This function is used in translating rhino3dm planar Brep to Ladybug Face3D objects.

    Args:
        brep: A rhino3dm Brep.
        tolerance: A rhino3dm tolerance object. Tolerance set in the rhino file.

    Returns:
        A list of Ladybug Face3D objects.
    """
    # Getting all vertices of the face
    mesh = brep.Faces[0].GetMesh(rhino3dm.MeshType.Any)
    if not mesh:
        raise AttributeError

    # * Check 01 - If any of the edge is an arc
    lines = []
    curved = False
    for i in range(len(brep.Edges)):
        if not brep.Edges[i].IsLinear(tolerance):
            curved = True
            break
    # If one of the edges is curved, mesh it
    if curved:
        return [brep_to_meshed_face3d(brep, tolerance)]
        return [brep_to_meshed_face3d(brep, tolerance)]

    elif len(mesh.Vertices) == 4 or len(mesh.Vertices) == 3:
        return [brep_to_meshed_face3d(brep, tolerance)]
        return [brep_to_meshed_face3d(brep, tolerance)]

    else:
        # Create Ladybug lines from start and end points of edges
        for i in range(len(brep.Edges)):
            start_pt = to_point3d(brep.Edges[i].PointAtStart)
            end_pt = to_point3d(brep.Edges[i].PointAtEnd)
            line = LineSegment3D.from_end_points(start_pt, end_pt)
            lines.append(line)

        # Create Ladybug Polylines from the lines
        polylines = Polyline3D.join_segments(lines, tolerance)

        # In the list of the Polylines, if there's only one polyline then
        # the face has no holes
        if len(polylines) == 1:
            # When accessing the vertices for a polyline, a duplicate vertice is
            # found in the tuple of vertices. This is fixed by using this 
            # remove_dup_vertices method
            boundary_pts = remove_dup_vertices(polylines[0].vertices, tolerance)
            if len(boundary_pts) < 3:
                raise ValueError
            else:
                return [Face3D(boundary=boundary_pts)]

        # In the list of the Polylines, if there's more than one polyline then
        # the face has hole / holes
        elif len(polylines) > 1:
            # while creating polylines from lines if lines are remaining,
            # mesh the geometry
            if not isinstance(polylines[-1], Polyline3D):
                return brep_to_mesh_to_face3d(brep)

            # while creating polylines from lines if lines are remaining,
            # mesh the geometry
            if not isinstance(polylines[-1], Polyline3D):
                return brep_to_mesh_to_face3d(brep)

            # Get the area of Face3D created by the polylines
            polyline_areas = [Face3D(polyline.vertices).area for polyline in polylines
                if isinstance(polyline, Polyline3D)]
            polyline_area_dict = dict(zip(polylines, polyline_areas))
            # Sort the Polylines based on area of face created from polyline vertices
            # The longest polyline belongs to the boundary of the face
            # The rest of the polylines belong to the holes in the face
            # The first polyline in the list shall always be the polyline for
            # the boundary
            sorted_dict = sorted(polyline_area_dict.items(),
                key=lambda x: x[1], reverse=True)
            sorted_polylines = [item[0] for item in sorted_dict]
            # Vertices for the boundary
            # When accessing the vertices for a polyline, a duplicate vertice is
            # found in the tuple of vertices. This is fixed by using this
            # remove_dup_vertices method
            boundary_pts = remove_dup_vertices(
                sorted_polylines[0].vertices, tolerance)
            # Vertices for the hole / holes
            hole_pts = [remove_dup_vertices(polyline.vertices, tolerance)
                        for polyline in sorted_polylines[1:]]
            # Merging lists of hole vertices
            total_hole_pts = [
                pts for pts_lst in hole_pts for pts in pts_lst]
            hole_pts_on_boundary = [
                pts for pts in total_hole_pts if pts in boundary_pts]

            # * Check 02 - If any of the hole is touching the boundary of the face
            if len(hole_pts_on_boundary) > 0:
                warnings.warn(
                    'A Brep has holes that touch the boundary of the brep.'
                    ' This geometry will be meshed.'
                    )
                return brep_to_mesh_to_face3d(brep)
            else:
                return [Face3D(boundary=boundary_pts, holes=hole_pts)]


def brepface_to_face3d(brepFace, tolerance):

    print(" ")
    mesh = brepFace.GetMesh(rhino3dm.MeshType.Any)

    curved = False
    for j in range(len(mesh.TopologyEdges)):
        if not isinstance(mesh.TopologyEdges.EdgeLine(j), rhino3dm.Line):
            curved = True
            break
    # If one of the edges is curved, mesh it
    if curved:
        print("It is curved")
        faces = mesh_to_face3d(mesh)
        try:
            polyface = Polyface3D.from_faces(faces, tolerance)
        except Exception:
            raise ValueError
        lines = list(polyface.naked_edges)
        polylines = Polyline3D.join_segments(lines, tolerance)
        face3d = Face3D(boundary=polylines[0].vertices)
        return [face3d]

    elif len(mesh.Vertices) == 4 or len(mesh.Vertices) == 3:
        print("It has 3 or 4 vertices")
        faces = mesh_to_face3d(mesh)
        try:
            polyface = Polyface3D.from_faces(faces, tolerance)
        except Exception:
            raise ValueError
        lines = list(polyface.naked_edges)
        polylines = Polyline3D.join_segments(lines, tolerance)
        face3d = Face3D(boundary=polylines[0].vertices)
        return [face3d]

    else:
        print("It has entered the last option")
        faces = mesh_to_face3d(mesh)
        try:
            polyface = Polyface3D.from_faces(faces, tolerance)
        except Exception:
            raise ValueError
        lines = list(polyface.naked_edges)
        polylines = Polyline3D.join_segments(lines, tolerance)
        check_polylines = [isinstance(polyline, Polyline3D) for polyline in polylines]
        if all(check_polylines):
            face3d = Face3D(boundary=polylines[0].vertices)
            return [face3d]
        else:
            return faces
        






        # lines = []
        # for k in range(len(mesh.TopologyEdges)):
        #     start_pt = to_point3d(mesh.TopologyEdges.EdgeLine(k).PointAt(0.0))
        #     end_pt = to_point3d(mesh.TopologyEdges.EdgeLine(k).PointAt(1.0))
        #     line = LineSegment3D.from_end_points(start_pt, end_pt)
        #     lines.append(line)

        # # # Create Ladybug Polylines from the lines
        # polylines = Polyline3D.join_segments(lines, tolerance)


        # if len(polylines) == 1:
        #     print("One polyline")
        #     boundary_pts1 = remove_dup_vertices(polylines[0].vertices, tolerance)
        #     boundary_pts = remove_dup_vertices(boundary_pts1, tolerance)
        #     print(boundary_pts)
        #     face3d = Face3D(boundary=boundary_pts)
        #     print (face3d)
        #     return []
        #     return [face3d]

        # elif len(polylines) > 1:
        #     print("More polylines")
        #     check_polylines = [isinstance(polyline, Polyline3D) for polyline in polylines]
        #     if not all(check_polylines):
        #         print("Line found in polylines")
        #         faces = mesh_to_face3d(mesh)
        #         return faces
        #     else:
        #         print("No Line at the end")
        #         polyline_areas = [Face3D(polyline.vertices).area for polyline in polylines
        #             if isinstance(polyline, Polyline3D)]

        #         polyline_area_dict = dict(zip(polylines, polyline_areas))
            
        #         sorted_dict = sorted(polyline_area_dict.items(), key=lambda x: x[1], reverse=True)
        #         sorted_polylines = [item[0] for item in sorted_dict]

        #         boundary_pts = remove_dup_vertices(
        #             sorted_polylines[0].vertices, tolerance)
        #         # Vertices for the hole / holes
        #         hole_pts = [remove_dup_vertices(polyline.vertices, tolerance)
        #                     for polyline in sorted_polylines[1:]]
        #         # Merging lists of hole vertices
        #         total_hole_pts = [
        #             pts for pts_lst in hole_pts for pts in pts_lst]
        #         hole_pts_on_boundary = [
        #             pts for pts in total_hole_pts if pts in boundary_pts]
                
        #         print(len(hole_pts_on_boundary), len(total_hole_pts))
        #         # * Check 02 - If any of the hole is touching the boundary of the face
        #         if len(hole_pts_on_boundary) == len(total_hole_pts):
        #             print("All hole points on boundary. Faces shall be merges.")
        #             faces = mesh_to_face3d(mesh)
        #             polyface = Polyface3D.from_faces(faces, tolerance)
        #             lines = list(polyface.naked_edges)
        #             polylines = Polyline3D.join_segments(lines, tolerance)
        #             face3d = Face3D(boundary=polylines[0].vertices)
        #             return [face3d]

        #         elif len(hole_pts_on_boundary) > 0:
        #             print("holes touching boundary")
        #             warnings.warn(
        #                 'A Brep has holes that touch the boundary of the brep.'
        #             ' This geometry will be meshed.'
        #                 )
        #             return []
        #             faces = mesh_to_face3d(mesh)

        #         else:
        #             print("holes not touching boundary")
        #             face3d = Face3D(boundary=boundary_pts, holes=hole_pts)
        #             return [face3d]

            
def brep_to_brepface_to_face3d(brep, tolerance):
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
        # normals = set([face.normal.z for face in faces])
        if not brep.Surfaces[i].IsPlanar(tolerance):
        # if len(normals) > 1:
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


def extrusion_to_face3d(extrusion):
    """Get a list of Ladybug Face3D objects from a rhino3dm Extrusion.

    Args:
        brep: A rhino3dm Extrusion.

    Returns:
        A list of Ladybug Face3D objects.
    """
    faces = []
    mesh = extrusion.GetMesh(rhino3dm.MeshType.Any)
    faces.extend(mesh_to_face3d(mesh))

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
    print (" ")
    print(rh_geo)

    # if it's a Brep
    if isinstance(rh_geo, rhino3dm.Brep):
        # If it's a solid brep
        if rh_geo.IsSolid:
            print("It is solid")
            lb_face = solid_to_face3d(rh_geo, tolerance)
        else:
            # If it's a planar brep
            if check_planarity(rh_geo, tolerance) and len(rh_geo.Faces) == 1:
                print("it is planar")
                lb_face = brep_to_face3d(rh_geo, tolerance)
            # If it's not a planar brep. Such as a curved wall
            else:
                print("it is not planar")
                # lb_face = brepface_to_face3d(rh_geo, tolerance)
                lb_face = brep_to_brepface_to_face3d(rh_geo, tolerance)

    # If it's an extrusion
    elif isinstance(rh_geo, rhino3dm.Extrusion):
            lb_face = extrusion_to_face3d(rh_geo)

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
