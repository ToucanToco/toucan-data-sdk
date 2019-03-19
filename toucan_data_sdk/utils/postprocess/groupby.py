from typing import Dict, List, Union


def groupby(df, *, group_cols: Union[str, List[str]], aggregations: Dict[str, str]):
    """
    Aggregate values by groups.

    ---

    ### Parameters

    *mandatory :*
    - `group_cols` (*list*): list of columns used to group data
    - `aggregations` (*dict*): dictionnary of values columns to group as keys and aggregation
      function to use as values (See the [list of aggregation functions](
      https://pandas.pydata.org/pandas-docs/stable/user_guide/groupby.html#aggregation))

    ---

    ### Example

    **Input**

    | ENTITY | YEAR | VALUE_1 | VALUE_2 |
    |:------:|:----:|:-------:|:-------:|
    |    A   | 2017 |    10   |    3    |
    |    A   | 2017 |    20   |    1    |
    |    A   | 2018 |    10   |    5    |
    |    A   | 2018 |    30   |    4    |
    |    B   | 2017 |    60   |    4    |
    |    B   | 2017 |    40   |    3    |
    |    B   | 2018 |    50   |    7    |
    |    B   | 2018 |    60   |    6    |

    ```cson
    groupby:
      group_cols: ['ENTITY', 'YEAR']
      aggregations:
        'VALUE_1': 'sum',
        'VALUE_2': 'mean'
    ```

    **Output**

    | ENTITY | YEAR | VALUE_1 | VALUE_2 |
    |:------:|:----:|:-------:|:-------:|
    |    A   | 2017 |    30   |   2.0   |
    |    A   | 2018 |    40   |   4.5   |
    |    B   | 2017 |   100   |   3.5   |
    |    B   | 2018 |   110   |   6.5   |

    """
    df = df.groupby(group_cols, as_index=False).agg(aggregations)
    return df
