[![Pypi-v](https://img.shields.io/pypi/v/toucan-data-sdk.svg)](https://pypi.python.org/pypi/toucan-data-sdk)
[![Pypi-pyversions](https://img.shields.io/pypi/pyversions/toucan-data-sdk.svg)](https://pypi.python.org/pypi/toucan-data-sdk)
[![Pypi-l](https://img.shields.io/pypi/l/toucan-data-sdk.svg)](https://pypi.python.org/pypi/toucan-data-sdk)
[![Pypi-wheel](https://img.shields.io/pypi/wheel/toucan-data-sdk.svg)](https://pypi.python.org/pypi/toucan-data-sdk)
[![CircleCI](https://img.shields.io/circleci/project/github/ToucanToco/toucan-data-sdk.svg)](https://circleci.com/gh/ToucanToco/toucan-data-sdk)
[![codecov](https://codecov.io/gh/ToucanToco/toucan-data-sdk/branch/master/graph/badge.svg)](https://codecov.io/gh/ToucanToco/toucan-data-sdk)

# Toucan Data SDK

Develop your Toucan Toco data pipeline from the confort of your favorite environment.

# Installation

`pip install toucan_data_sdk`

# Usage

## Get data sources

```python
import getpass
from toucan_data_sdk import ToucanDataSdk

instance_url = 'https://api-demo.toucantoco.com'
small_app = 'demo'
auth = ('<username>', getpass.getpass())

sdk = ToucanDataSdk(instance_url, small_app=small_app, auth=auth)
dfs = sdk.get_dfs()
```

# API

## ToucanDataSdk class

### ToucanDataSdk.get_dfs()

Uses the client to send a request to the backend to send the data sources 
as DataFrames (uses an internal cache).

### ToucanDataSdk.invalidate_cache()

Invalidates the cache. Next time you will `get_dfs`, a 
request will be sent to the backend.

### Utils

cf. https://docs.toucantoco.com/concepteur/data-sources/00-generalities.html#utility-functions

For example:

```python
from toucan_data_sdk.utils import add_missing_row
```

# Development

## Makefile

Use the makefile to `test`, `build`...

```shell
$ make test
```

# Development

## PEP8

New code must be PEP8-valid (with a maximum of 100 chars): tests wont pass if code is not.
To see PEP8 errors, run `pycodestyle <path_to_file_name>` or recursively: `pycodestyle -r .`
