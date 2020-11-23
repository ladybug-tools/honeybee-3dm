[![Build Status](https://travis-ci.com/ladybug-tools/honeybee-3dm.svg?branch=master)](https://travis-ci.com/ladybug-tools/honeybee-3dm)
[![Coverage Status](https://coveralls.io/repos/github/ladybug-tools/honeybee-3dm/badge.svg?branch=master)](https://coveralls.io/github/ladybug-tools/honeybee-3dm)

[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)

# honeybee-3dm

Honeybee extension for translating to and from [Rhino 3dm](https://www.rhino3d.com/).

## Installation

```console
pip install -U honeybee-3dm
```

## QuickStart

```python
import honeybee_3dm

```

## [API Documentation](http://ladybug-tools.github.io/honeybee-3dm/docs)

## Local Development

1. Clone this repo locally
```console
git clone git@github.com:ladybug-tools/honeybee-3dm

# or

git clone https://github.com/ladybug-tools/honeybee-3dm
```
2. Install dependencies:
```console
cd honeybee-3dm
pip install -r dev-requirements.txt
pip install -r requirements.txt
```

3. Run Tests:
```console
python -m pytest tests/
```

4. Generate Documentation:
```console
sphinx-apidoc -f -e -d 4 -o ./docs ./honeybee_3dm
sphinx-build -b html ./docs ./docs/_build/docs
```
