
# honeybee-3dm
Honeybee extension for translating from a [Rhino 3dm](https://www.rhino3d.com/) aka,
a Rhino file.

[![Build Status](https://github.com/ladybug-tools/honeybee-3dm/workflows/CI/badge.svg)](https://github.com/ladybug-tools/honeybee-3dm/actions)
[![Coverage Status](https://coveralls.io/repos/github/ladybug-tools/honeybee-3dm/badge.svg)](https://coveralls.io/github/ladybug-tools/honeybee-3dm)
[![Python 3.7](https://img.shields.io/badge/python-3.7-green.svg)](https://www.python.org/downloads/release/python-370/)

## Installation

```console
pip install honeybee-3dm
```

## QuickStart

```python
import honeybee_3dm
```
## Usage

```console
Usage: honeybee-3dm translate [OPTIONS] RHINO_FILE

  Translate a rhino file to HBJSON.

  Args:
      rhino-file: Path to the rhino file.

Options:
  -n, --name TEXT         Name of the output HBJSON file. If not provided,
                          "unnamed" will be used.

  -f, --folder DIRECTORY  Path to folder where HBJSON will be written.
                          [default: .]

  -cf, --config PATH      File Path to the config.json file.
  --help                  Show this message and exit.
```

## Connection
After generating the hbjson, you may use
[honeybee-vtk](https://github.com/ladybug-tools/honeybee-vtk#honeybee-vtk) to visualize
that hbjson in a web browser.

## [API Documentation](http://ladybug-tools.github.io/honeybee-3dm/docs)
