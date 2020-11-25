"""This module parsers the config.json file."""
import json


def read_json(path):
    with open(path) as fh:
        config = json.load(fh)
        return config

