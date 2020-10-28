"""Functions to create Ladybug geometries from Rhino geometries."""

from ladybug_geometry.geometry3d.pointvector import Vector3D, Point3D
from ladybug_geometry.geometry3d.line import LineSegment3D
from ladybug_geometry.geometry3d.mesh import Mesh3D
from ladybug_geometry.geometry3d.face import Face3D
from ladybug_geometry.geometry3d.polyface import Polyface3D

import ladybug.color as lbc


def to_point3d(point):
    """Ladybug Point3D from Rhino Point3d."""
    pass


def to_linesegment3d(line):
    """Ladybug LineSegment3D from Rhino LineCurve."""
    pass


def to_face3d(geo):
    """List of Ladybug Face3D objects from a Rhino Brep, Surface or Mesh."""
    pass


def to_polyface3d(geo):
    """A Ladybug Polyface3D object from a Rhino Brep."""
    pass


def to_mesh3d(mesh):
    """Ladybug Mesh3D from Rhino Mesh."""
    pass
