def argmax(df, column: str):
    """
    Keep the row of the data corresponding to the maximal value in a column

    ---

    ### Parameters

    *mandatory :*
    - `column` (*str*): name of the column containing the value you want to keep the maximum

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
    df = df[df[column] == df[column].max()]
    return df


def argmin(df, column: str):
    """
    Keep the row of the data corresponding to the minimal value in a column

    ---

    ### Parameters

    *mandatory :*
    - `column` (str): name of the column containing the value you want to keep the minimum

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
    df = df[df[column] == df[column].min()]
    return df
