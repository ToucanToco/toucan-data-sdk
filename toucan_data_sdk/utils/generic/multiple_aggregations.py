import pandas as pd
import itertools


def multiple_aggregations(
    df,
    id_cols,
    requesters,
    agg_func='sum'
):
    """
    Aggregates data to reproduce "All" category for requester
    - `id_cols` are the columns id to group,
    - `requesters` is a dict with the colums corresponding to
       the filters as key and their default value as value
    - `agg_func` (optional) is the function to use for aggregating the data.
       Can be callable, string, dictionary, or list of string/callables (by default 'sum')
    """
    requesters_cols = list(requesters.keys())
    requester_combination = [
        list(item) for i in range(0, len(requesters_cols) + 1)
        for item in itertools.combinations(requesters_cols, i)]
    dfs_result = []
    for comb in requester_combination:
        df_tmp = df.groupby(id_cols + comb).agg(agg_func).reset_index()
        for key in (set(requesters.keys()) - set(comb)):
            df_tmp[key] = requesters[key]
        dfs_result.append(df_tmp)

    return pd.concat(dfs_result)
