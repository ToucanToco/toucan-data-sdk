import itertools
from typing import Dict, List, Union

import pandas as pd


def combine_columns_aggregation(
    df,
    id_cols: List[str],
    cols_for_combination: Dict[str, str],
    agg_func: Union[str, List[str], Dict[str, str]] = 'sum',
):
    """
    Aggregates data to reproduce "All" category for requester

    ---

    ### Parameters

    *mandatory :*
    - `id_cols` (*list*): the columns id to group
    - `cols_for_combination` (*dict*): colums corresponding to
       the filters as key and their default value as value

    *optional :*
    - `agg_func` (*str*, *list* or *dict*): the function(s) to use for aggregating the data.
       Accepted combinations are:
       - string function name
       - list of functions and/or function names, e.g. [np.sum, 'mean']
       - dict of axis labels -> functions, function names or list of such.
    """
    requesters_cols = list(cols_for_combination.keys())
    requester_combination = [
        list(item)
        for i in range(0, len(requesters_cols) + 1)
        for item in itertools.combinations(requesters_cols, i)
    ]
    dfs_result = []
    for comb in requester_combination:
        df_tmp = df.fillna(method='ffill').groupby(id_cols + comb).agg(agg_func).reset_index()
        for key in set(cols_for_combination.keys()) - set(comb):
            df_tmp[key] = cols_for_combination[key]
        dfs_result.append(df_tmp)

    return pd.concat(dfs_result, sort=False, ignore_index=True)
