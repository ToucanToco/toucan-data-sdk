# Touca Data SDK



# Usage

```python
from toucan_client import ToucanClient
from toucan_data_sdk import ToucanDataSdk
from toucan_data_sdk.utils import add_missing_row

# Get DataFrames
client = ToucanClient('base_url')
sdk = ToucanDataSdk(client)
dfs = sdk.dfs

# Use some utils functions
df = dfs['some_key']
df = add_missing_row(df, id_cols=['NAME'], reference_col='MONTH')
```

# Development

## PEP8

New code must be PEP8-valid (with a maximum of 100 chars): tests wont pass if code is not.
To see PEP8 errors, run `pycodestyle <path_to_file_name>` or recursively: `pycodestyle -r .`
