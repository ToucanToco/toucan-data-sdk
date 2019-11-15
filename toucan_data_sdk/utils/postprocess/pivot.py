from typing import List

import numpy as np
import pandas as pd

from toucan_data_sdk.utils.helpers import get_temp_column_name


def pivot(
    df,
    index: List[str],
    column: str,
    value: str,
    agg_function: str = 'mean',
    values_to_pivot: List[str] = None,
):
    """
    Pivot the data. Reverse operation of melting

    ---

    ### Parameters

    *mandatory :*
    - `index` (*list*): names of index columns.
    - `column` (*str*): column name to pivot on
    - `value` (*str*): column name containing the value to fill the pivoted df

    *optional :*
    - `agg_function` (*str*): aggregation function to use among 'mean' (default), 'count', 'mean', 'max', 'min'
    - `values_to_pivot` (*list of str*): select the value in `column` to pivot
    ---

    ### Example

    **Input**

    | variable |   wave  |  year    | value |
    |:--------:|:-------:|:--------:|:-----:|
    |   toto   |  wave 1 |  2014    |  300  |
    |   toto   |  wave 1 |  2015    |  250  |
    |   toto   |  wave 1 |  2016    |  450  |

    ```cson
    pivot:
      index: ['variable','wave']
      column: 'year'
      value: 'value'
    ```

    **Output**

    | variable |   wave  |  2014  | 2015 | 2015 |
    |:--------:|:-------:|:------:|:----:|:----:|
    |   toto   |  wave 1 |  300   | 250  | 450  |
    """
    if df.dtypes[value].type == np.object_:
        # Force the value column to be str-only (because mixed dtypes causes errors)
        df[value] = df[value].astype(str)
        df = pd.pivot_table(
            df, index=index, columns=column, values=value, aggfunc=lambda x: ' '.join(x)
        )
    else:
        df = pd.pivot_table(df, index=index, columns=column, values=value, aggfunc=agg_function)
    df = df.reset_index()
    if values_to_pivot:
        df = df.melt(
            id_vars=index + values_to_pivot,
            value_vars=df.columns.difference(index + values_to_pivot),
        )
    return df


def pivot_by_group(df, variable, value, new_columns, groups, id_cols=None):
    """
    Pivot a dataframe by group of variables

    ---

    ### Parameters

    *mandatory :*
    * `variable` (*str*): name of the column used to create the groups.
    * `value` (*str*): name of the column containing the value to fill the pivoted df.
    * `new_columns` (*list of str*): names of the new columns.
    * `groups` (*dict*): names of the groups with their corresponding variables.
      **Warning**: the list of variables must have the same order as `new_columns`

    *optional :*
    * `id_cols` (*list of str*) : names of other columns to keep, default `None`.

    ---

    ### Example

    **Input**

    | type |  variable  | montant |
    |:----:|:----------:|:-------:|
    |   A  |    var1    |    5    |
    |   A  | var1_evol  |   0.3   |
    |   A  |    var2    |    6    |
    |   A  | var2_evol  |   0.2   |

    ```cson
    pivot_by_group :
      id_cols: ['type']
      variable: 'variable'
      value: 'montant'
      new_columns: ['value', 'variation']
      groups:
        'Group 1' : ['var1', 'var1_evol']
        'Group 2' : ['var2', 'var2_evol']
    ```

    **Ouput**

    | type |  variable  |  value  | variation |
    |:----:|:----------:|:-------:|:---------:|
    |   A  |   Group 1  |    5    |    0.3    |
    |   A  |   Group 2  |    6    |    0.2    |

    """
    df = df.copy()

    if id_cols is None:
        index = [variable]
    else:
        index = [variable] + id_cols

    param = pd.DataFrame(groups, index=new_columns)

    temporary_colum = get_temp_column_name(df)
    df[temporary_colum] = df[variable]
    for column in param.columns:
        df.loc[df[variable].isin(param[column]), variable] = column

    param = param.T
    for column in param.columns:
        df.loc[df[temporary_colum].isin(param[column]), temporary_colum] = column

    df = pivot(df, index, temporary_colum, value)
    return df
