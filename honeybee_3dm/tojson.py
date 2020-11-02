try:  # import the core honeybee dependencies
    from honeybee.model import Model
    from honeybee.config import folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

import os
import json


def publish_json(_hb_objs, _name_=None, _folder_=None, indent_=None, abridged_=False, _dump=True):

    # set the component defaults
    name = _name_ if _name_ is not None else 'unnamed'
    file_name = '{}.json'.format(name) if len(_hb_objs) > 1 or not \
        isinstance(_hb_objs[0], Model) else '{}.hbjson'.format(name)

    folder = _folder_ if _folder_ is not None else folders.default_simulation_folder
    hb_file = os.path.join(folder, file_name)
    indent = indent_ if indent_ is not None else 0
    abridged = bool(abridged_)

    # create the dictionary to be written to a JSON file
    if len(_hb_objs) == 1:  # write a single object into a file if the length is 1
        try:
            obj_dict = _hb_objs[0].to_dict(abridged=abridged)
        except TypeError:  # no abridged option
            obj_dict = _hb_objs[0].to_dict()
    else:  # create a dictionary of the objects that are indexed by name
        obj_dict = {}
        for obj in _hb_objs:
            try:
                obj_dict[obj.identifier] = obj.to_dict(abridged=abridged)
            except TypeError:  # no abridged option
                obj_dict[obj.identifier] = obj.to_dict()

    # write the dictionary into a file
    with open(hb_file, 'w') as fp:
        json.dump(obj_dict, fp, indent=indent)
