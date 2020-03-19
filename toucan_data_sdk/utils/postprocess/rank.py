from typing import List, Union

import numpy as np


def rank(
    df,
    value_cols: Union[str, List[str]],
    group_cols: List[str] = None,
    rank_cols_names: List[str] = None,
    method='min',
    ascending: bool = True,
):
    """
    This function creates rank columns based on numeric values to be ranked.

    ---

    ### Parameters

    *mandatory :*
    - `value_cols` (*list*): name(s) of the columns used

    *optional :*
    - `group_cols` (*list*): name(s) of the column(s) used to
      create each group inside which independent ranking needs to be applied
    - `rank_cols_names` (*list*): the names of the added ranking columns.
      If not filled, the ranking will be named after the value_cols with a '_rank' suffix
    - `method` (*str*): method to use when encountering equal values:
        - `'min'` (default): lowest rank in group
        - `'max'`: highest rank in group
        - `'average'`: average rank of group
        - `'first'`: ranks assigned in order the values appear in the series
        - `'dense'`: like 'min', but rank always increases by 1 between groups
    - `ascending` (*boolean*): whether the rank should be determined based on
       ascending (default) or descending order

    ---

    ### Example

    **Input**

    | ENTITY | YEAR | VALUE_1 | VALUE_2 |
    | :---: | :---: | :---: | :---: |
    | A | 2017 | 10 | 3 |
    | A | 2017 | 20 | 1 |
    | A | 2018 | 10 | 5 |
    | A | 2018 | 30 | 4 |
    | B | 2017 | 60 | 4 |
    | B | 2017 | 40 | 3 |
    | B | 2018 | 50 | 7 |
    | B | 2018 | 50 | 6 |

    ```cson
    rank :
      value_cols: 'VALUE_1'
    ```

    **Output**

    | ENTITY | YEAR | VALUE_1 | VALUE_2 | VALUE_1_rank
    | :---: | :---: | :---: | :---: | :---: |
    | A | 2017 | 10 | 3 | 1 |
    | A | 2017 | 20 | 1 | 3 |
    | A | 2018 | 10 | 5 | 1 |
    | A | 2018 | 30 | 4 | 4 |
    | B | 2017 | 60 | 4 | 8 |
    | B | 2017 | 40 | 3 | 5 |
    | B | 2018 | 50 | 7 | 6 |
    | B | 2018 | 50 | 6 | 6 |
    """

    value_cols = [value_cols] if not isinstance(value_cols, list) else value_cols
    for col in value_cols:
        if not np.issubdtype(df[col].dtype, np.number):
            raise TypeError(f'{col} specified in value_cols must be of numeric type')

    if rank_cols_names is None:
        rank_cols_names = [x + '_rank' for x in value_cols]

    if group_cols is None:
        df[rank_cols_names] = df[value_cols].rank(method=method, ascending=ascending)
    else:
        df[rank_cols_names] = df.groupby(group_cols)[value_cols].rank(
            method=method, ascending=ascending
        )

    if method != 'average':
        df[rank_cols_names] = df[rank_cols_names].astype('int')

    return df
