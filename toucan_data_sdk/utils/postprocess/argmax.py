from typing import List, Union


def argmax(df, column: str, groups: Union[str, List[str]] = None):
    """
    Keep the row of the data corresponding to the maximal value in a column

    ---

    ### Parameters

    *mandatory :*
    - `column` (*str*): name of the column containing the value you want to keep the maximum

    *optional :*
    - `groups` (*str or list(str)*): name of the column(s) used for 'groupby' logic
    (the function will return the argmax by group)

    ---

    ### Example

    **Input**

    | variable |   wave  |  year    | value |
    |:--------:|:-------:|:--------:|:-----:|
    |   toto   |  wave 1 |  2014    |  300  |
    |   toto   |  wave 1 |  2015    |  250  |
    |   toto   |  wave 1 |  2016    |  450  |

    ```cson
    argmax:
      column: 'year'
    ```

    **Output**

    | variable |   wave  |  year    | value |
    |:--------:|:-------:|:--------:|:-----:|
    |   toto   |  wave 1 |  2016    |  450  |
    """
    if groups is None:
        df = df[df[column] == df[column].max()].reset_index(drop=True)
    else:
        group_max = df.groupby(groups)[column].transform('max')
        df = df.loc[df[column] == group_max, :].drop_duplicates().reset_index(drop=True)
    return df


def argmin(df, column: str, groups: Union[str, List[str]] = None):
    """
    Keep the row of the data corresponding to the minimal value in a column

    ---

    ### Parameters

    *mandatory :*
    - `column` (str): name of the column containing the value you want to keep the minimum

    *optional :*
    - `groups` (*str or list(str)*): name of the column(s) used for 'groupby' logic
    (the function will return the argmax by group)
    ---

    ### Example

    **Input**

    | variable |   wave  |  year    | value |
    |:--------:|:-------:|:--------:|:-----:|
    |   toto   |  wave 1 |  2014    |  300  |
    |   toto   |  wave 1 |  2015    |  250  |
    |   toto   |  wave 1 |  2016    |  450  |

    ```cson
    argmin:
      column: 'year'
    ]
    ```

    **Output**

    | variable |   wave  |  year    | value |
    |:--------:|:-------:|:--------:|:-----:|
    |   toto   |  wave 1 |  2015    |  250  |
    """
    if groups is None:
        df = df[df[column] == df[column].min()].reset_index(drop=True)
    else:
        group_min = df.groupby(groups)[column].transform('min')
        df = df.loc[df[column] == group_min, :].drop_duplicates().reset_index(drop=True)
    return df
