import pandas as pd
from typing import List


def roll_up(
        df,
        levels: List[str],
        groupby_vars: List[str],
        extra_groupby_cols: List[str] = None,
        var_name: str = 'type',
        value_name: str = 'value',
        agg_func: str = 'sum',
        drop_levels: List[str] = None
):
    """
    Creates aggregates following a given hierarchy

    ---

    ### Parameters

    *mandatory :*
    - `levels` (*list of str*): name of the columns composing the hierarchy (from the top to the bottom level).
    - `groupby_vars` (*list of str*): name of the columns with value to aggregate.
    - `extra_groupby_cols` (*list of str*) optional: other columns used to group in each level.

    *optional :*
    - `var_name` (*str*) : name of the result variable column. By default, `“type”`.
    - `value_name` (*str*): name of the result value column. By default, `“value”`.
    - `agg_func` (*str*): name of the aggregation operation. By default, `“sum”`.
    - `drop_levels` (*list of str*): the names of the levels that you may want to discard from the output.

    ---

    ### Example

    **Input**

    |    Region |     City |  Population |
    |:---------:|:--------:|:-----------:|
    |       Idf |     Panam|         200 |
    |       Idf |   Antony |          50 |
    |      Nord |    Lille |          20 |

    ```cson
    roll_up:
      levels: ["Region", "City"]
      groupby_vars: "Population"
    ```

    **Output**

    |    Region |     City |  Population |    value |   type |
    |:---------:|:--------:|:-----------:|:--------:|:------:|
    |       Idf |     Panam|         200 |    Panam |   City |
    |       Idf |   Antony |          50 |   Antony |   City |
    |      Nord |    Lille |          20 |    Lille |   City |
    |       Idf |      Nan |         250 |      Idf | Region |
    |      Nord |      Nan |          20 |     Nord | Region |
    """
    dfs = list()
    groupby_cols_cpy = list(levels)
    levels_cpy = list(levels)
    levels_cpy.reverse()

    extra_groupby_cols = extra_groupby_cols or []
    drop_levels = drop_levels or []
    previous_level = None
    for top_level in levels_cpy:
        # Aggregation
        gb_df = getattr(
            df.groupby(groupby_cols_cpy + extra_groupby_cols)[groupby_vars],
            agg_func)().reset_index()

        # Melt-like columns
        gb_df[var_name] = top_level
        gb_df[value_name] = gb_df[top_level]
        dfs.append(gb_df)
        if previous_level in drop_levels:
            del dfs[-2]
        previous_level = top_level

        # Remove one level each time in the groupby: lowest level column needs
        # a groupby with every levels, the next level needs every one except
        # the lowest, etc. until the top level column that needs only itself
        # inside the groupby.
        groupby_cols_cpy.pop()
    return pd.concat(dfs, sort=False).reset_index()
