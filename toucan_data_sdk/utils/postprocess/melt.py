from typing import List

import pandas as pd


def melt(df, id: List[str], value: List[str], dropna=False):
    """
    A melt will transform a dataset by creating a column "variable" and a column "value".
    This function is useful to transform a dataset into a format where one or more columns
    are identifier variables, while all other columns, considered measured
    variables (value_vars), are “unpivoted” to the row axis, leaving just two
    non-identifier columns, `"variable"` and `"value"`.

    ---

    ### Parameters

    *mandatory :*
    - `id` (*list of str*): names of the columns that must be kept in column.
    - `value` (*list of str*): names of the columns that will be transformed in long format (in rows).

    *optional :*
    - `dropna` (*boolean*): It allows you to drop missing values.

    ---

    ### Example

    **Input**

    | my_label | my_value | my_column_1 | my_column_2 | info_1 | info_2 | info_3 |
    |:--------:|:--------:|:-----------:|:-----------:|:------:|:------:|:------:|
    |   toto   |    10    |     S45     |    Lalaland |   10   |   20   |  None  |

    ```cson
    melt:
      id: ['my_label', 'my_value' 'my_column_1', 'my_colum_2']
        value: ['info_1', 'info_2', 'info_3']
        dropna: true
    ```

    **Ouput**

    | my_label | my_value | my_column_1 | my_column_2 | variable | value  |
    |:--------:|:--------:|:-----------:|:-----------:|:--------:|:------:|
    |   toto   |    10    |     S45     |    Lalaland |  info_1  |   10   |
    |   toto   |    10    |     S45     |    Lalaland |  info_2  |   20   |
    """
    df = df[(id + value)]
    df = pd.melt(df, id_vars=id, value_vars=value)
    if dropna:
        df = df.dropna(subset=['value'])

    return df
