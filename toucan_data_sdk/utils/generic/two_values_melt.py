import pandas as pd
from typing import List


def two_values_melt(df, first_value_vars: List[str], second_value_vars: List[str], var_name: List[str], value_name: str):
    """
    First, build two DataFrames from the original one: one to compute a melt
    for the value, another one to compute a melt for the evolution. Second,
    merge these two DataFrames.

    - first_value_vars: value_vars of a pandas melt, for the first
        value columns of the DataFrame
    - second_value_vars: value_vars of a pandas melt, for the second
        value columns of the DataFrame
    - var_name: var_names of a pandas melt
    - value_name: value_name of a pandas melt


    # Examples #

    input :

    | ... | <some1> | <some2> | <some1_evol> | <some2_evol> |
    | ... | <val1>  | <val2>  | <evol1>      | <evol2>      |

    output :

    | ... | variable  | value  | evolution
    | ... | --------- | ------ | ---------
    | ... |  <some1>  | <val1> | <evol1>
    | ... |  <some2>  | <val2> | <evol2>
    """
    value_name_first = value_name + '_first'
    value_name_second = value_name + '_second'

    # Melt on the first value columns
    melt_first_value = pd.melt(df,
                               id_vars=[col for col in list(df) if
                                        col not in first_value_vars],
                               value_vars=first_value_vars,
                               var_name=var_name,
                               value_name=value_name_first)
    melt_first_value.drop(second_value_vars, axis=1, inplace=True)

    # Melt on the second value columns
    melt_second_value = pd.melt(df,
                                id_vars=[col for col in list(df) if
                                         col not in second_value_vars],
                                value_vars=second_value_vars,
                                var_name=var_name,
                                value_name=value_name_second)

    # Since there are two value columns, there is no need to keep the
    # second_value_vars names. And it will make things easier for the merge.
    normalize_types = {k: v for k, v in zip(second_value_vars, first_value_vars)}
    melt_second_value.replace(normalize_types, inplace=True)
    melt_second_value.drop(first_value_vars, axis=1, inplace=True)

    on_cols = list(melt_first_value)
    on_cols.remove(value_name_first)
    return pd.merge(melt_first_value, melt_second_value, on=on_cols, how='outer')
