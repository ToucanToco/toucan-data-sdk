[![Pypi-v](https://img.shields.io/pypi/v/toucan-data-sdk.svg)](https://pypi.python.org/pypi/toucan-data-sdk)
[![Pypi-pyversions](https://img.shields.io/pypi/pyversions/toucan-data-sdk.svg)](https://pypi.python.org/pypi/toucan-data-sdk)
[![Pypi-l](https://img.shields.io/pypi/l/toucan-data-sdk.svg)](https://pypi.python.org/pypi/toucan-data-sdk)
[![Pypi-wheel](https://img.shields.io/pypi/wheel/toucan-data-sdk.svg)](https://pypi.python.org/pypi/toucan-data-sdk)
[![CircleCI](https://img.shields.io/circleci/project/github/ToucanToco/toucan-data-sdk.svg)](https://circleci.com/gh/ToucanToco/toucan-data-sdk)
[![codecov](https://codecov.io/gh/ToucanToco/toucan-data-sdk/branch/master/graph/badge.svg)](https://codecov.io/gh/ToucanToco/toucan-data-sdk)

# Installation

`pip install toucan_data_sdk`

# Usage

```python
from toucan_client import ToucanClient
from toucan_data_sdk import ToucanDataSdk
from toucan_data_sdk.utils import add_missing_row

# Setup client
# Auth example
# from requests.auth import HTTPBasicAuth
# auth = HTTPBasicAuth('id', 'password')
client = ToucanClient('base_url', auth=auth)  # e.g. https://<api_route>/<small_app>
client.stage = 'staging'

# Get DataFrames
sdk = ToucanDataSdk(client)
dfs = sdk.dfs

# Use some utils functions
df = dfs['some_key']
df = add_missing_row(df, id_cols=['NAME'], reference_col='MONTH')
```

# API

## ToucanDataSdk class

### ToucanDataSdk.sdk

* property,
* uses the client to send a request to the back end to send the data sources 
as DataFrames,
* uses an internal cache.

### ToucanDataSdk.invalidate_cache()

Invalidates the cache. Next time you will access to the sdk property, a 
request will be sent to the client.

# Development

## PEP8

New code must be PEP8-valid (with a maximum of 100 chars): tests wont pass if code is not.
To see PEP8 errors, run `pycodestyle <path_to_file_name>` or recursively: `pycodestyle -r .`
