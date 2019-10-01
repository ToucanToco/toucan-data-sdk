from typing import List

import pandas as pd


def two_values_melt(
    df, first_value_vars: List[str], second_value_vars: List[str], var_name: str, value_name: str
):
    """
    Transforms one or multiple columns into rows.
    Unlike melt function, two value columns can be returned by
    the function (e.g. an evolution column and a price column)

    ---

    ### Parameters

    *mandatory :*
    - `first_value_vars` (*list of str*): name of the columns corresponding to the first returned value column
    - `second_value_vars` (*list of str*): name of the columns corresponding to the second returned value column
    - `var_name` (*str*): name of the column containing values in first_value_vars
    - `value_name` (*str*): suffix of the two value columns (suffix_first / suffix_second)
    ---

    ### Example

    **Input**

    |    Region |      avg |       total |  evo_avg |   evo_total |
    |:---------:|:--------:|:-----------:|:--------:|:-----------:|
    |         A |        50|         100 |        1 |           4 |
    |         B |       40 |         250 |        2 |           5 |


    ```cson
    two_values_melt:
      first_value_vars: ["avg", "total"]
      second_value_vars: ["evo_avg", "evo_total"]
      var_name: "type"
      value_name: "value"
    ```

    **Output**

    |    Region |     type |  value_first |  value_second |
    |:---------:|:--------:|:------------:|:-------------:|
    |         A |       avg|           50 |             1 |
    |         A |     total|          100 |             4 |
    |         B |       avg|           40 |             2 |
    |         B |       avg|          250 |             5 |
    """
    value_name_first = value_name + '_first'
    value_name_second = value_name + '_second'

    # Melt on the first value columns
    melt_first_value = pd.melt(
        df,
        id_vars=[col for col in list(df) if col not in first_value_vars],
        value_vars=first_value_vars,
        var_name=var_name,
        value_name=value_name_first,
    )
    melt_first_value.drop(second_value_vars, axis=1, inplace=True)

    # Melt on the second value columns
    melt_second_value = pd.melt(
        df,
        id_vars=[col for col in list(df) if col not in second_value_vars],
        value_vars=second_value_vars,
        var_name=var_name,
        value_name=value_name_second,
    )

    # Since there are two value columns, there is no need to keep the
    # second_value_vars names. And it will make things easier for the merge.
    normalize_types = {k: v for k, v in zip(second_value_vars, first_value_vars)}
    melt_second_value.replace(normalize_types, inplace=True)
    melt_second_value.drop(first_value_vars, axis=1, inplace=True)

    on_cols = list(melt_first_value)
    on_cols.remove(value_name_first)
    return pd.merge(melt_first_value, melt_second_value, on=on_cols, how='outer')
