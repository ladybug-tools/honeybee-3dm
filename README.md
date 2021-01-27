
# honeybee-3dm

Honeybee extension for translating from a [Rhino 3dm](https://www.rhino3d.com/) aka,
a Rhino file.

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
Usage: honeybee-3dm write [OPTIONS] RHINO_FILE

  Write an HBJSON from a rhino file. Args:     rhino-file: Path to the
  rhino file.

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
