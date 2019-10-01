from typing import List

from toucan_data_sdk.utils.helpers import check_params_columns_duplicate


def compute_ffill_by_group(df, id_cols: List[str], reference_cols: List[str], value_col: str):
    """
    Compute `ffill` with `groupby`
    Dedicated method as there is a performance issue with a simple groupby/fillna (2017/07)
    The method `ffill` propagates last valid value forward to next values.

    ---

    ### Parameters

    *mandatory :*
    - `id_cols` (*list of str*): names of columns used to create each group.
    - `reference_cols` (*list of str*): names of columns used to sort.
    - `value_col` (*str*): name of the columns to fill.

    ---

    ### Example

    **Input**

    name | rank | value
    :------:|:--------------:|:--------:
    A | 1 | 2
    A | 2 | 5
    A | 3 | null
    B | 1 | null
    B | 2 | 7

    ```cson
    compute_ffill_by_group:
      id_cols: ['name']
      reference_cols: ['rank']
      value_col: 'value'
    ```

    **Ouput**

    name | rank | value
    :------:|:--------------:|:--------:
    A | 1 | 2
    A | 2 | 5
    A | 3 | 5
    B | 1 | null
    B | 2 | 7
    """
    check_params_columns_duplicate(id_cols + reference_cols + [value_col])
    df = df.sort_values(by=id_cols + reference_cols)
    df = df.set_index(id_cols)
    df['fill'] = 1 - df[value_col].isnull().astype(int)
    df['fill'] = df.groupby(level=list(range(0, len(id_cols) - 1)))['fill'].cumsum()
    df[value_col] = df[value_col].ffill()
    df.loc[df['fill'] == 0, value_col] = None
    del df['fill']
    return df.reset_index()
