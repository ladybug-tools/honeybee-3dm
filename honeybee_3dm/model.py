"""Creating Honeybee model objects from rhino3dm surfces and closed volumes"""

# The Rhino3dm library provides the ability to access content of a Rhino3dm
# file from outside of Rhino
import rhino3dm

# Importing core Honeybee dependency
from honeybee.model import Model

# Importing dependencies from Honeybee-3dm package
from .face import to_face
from .grid import to_grid


def to_model(path, name="unnamed"):
    """Creates Honeybee models from a rhino3dm file.

    This function outputs a Honeybee model from the faces, shades, apertures, and doors
    on a rhino3dm file. Currently, this method works with faces only. In future,
    this method will support translating close volumes in Honeybee models as well.

    Args:
        path: A text string for the path to the rhino3dm file.
        name: A text string that will be used as the name of the Honeybee
            model.

    Returns:
        A Honeybee model.
    """
    # TODO create a quality check for the file path
    # TODO create a quality check for the file name
    rhino3dm_file = rhino3dm.File3dm.Read(path)

    if rhino3dm_file is not None:
        model_tolerance = rhino3dm_file.Settings.ModelAbsoluteTolerance
        model_angle_tolerance = rhino3dm_file.Settings.ModelAngleToleranceDegrees
        file_unit = rhino3dm_file.Settings.ModelUnitSystem
        if str(file_unit).split(".")[-1] not in ["Meters", "Millimeters",
                                                 "Feet", "Inches", "Centimeters"]:
            raise Exception("The unit of the Rhino file must be either of the following,"
                            " Meters, Millimeters, Feet, Inches, and Centimeters.")
        else:
            # Honeybee faces
            hb_face = to_face(rhino3dm_file, model_tolerance)
            # Honeybee grids
            hb_grid = to_grid(rhino3dm_file, model_tolerance)
            # Honeybee model
            model_unit = str(file_unit).split(".")[-1]
            hb_model = Model.from_objects(name, hb_face, units=model_unit,
                                          tolerance=model_tolerance,
                                          angle_tolerance=model_angle_tolerance)
            # Assigning grids to Honeybee model
            hb_model.properties.radiance.sensor_grids = hb_grid
            # Writing Honeybee model to a Radiance folder
            return hb_model
    else:
        raise Exception('A Rhino3dm file is not found.')
