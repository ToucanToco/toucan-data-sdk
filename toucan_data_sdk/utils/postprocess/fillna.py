from numpy import nan


def fillna(df, column: str, value=None, column_value=None):
    """
    Can fill NaN values from a column with a given value or a column

    ---

    ### Parameters

    - `column` (*str*): name of column you want to fill
    - `value`: NaN will be replaced by this value
    - `column_value`: NaN will be replaced by value from this column

    *NOTE*: You must set either the 'value' parameter or the 'column_value' parameter

    ---

    ### Example

    **Input**

    | variable |   wave  |  year    | my_value |
    |:--------:|:-------:|:--------:|:--------:|
    |   toto   |  wave 1 |  2014    |  300     |
    |   toto   |  wave 1 |  2015    |          |
    |   toto   |  wave 1 |  2016    |  450     |

    ```cson
    fillna:
      column: 'my_value'
      value: 0
    ```

    **Output**

    | variable |   wave  |  year    | my_value |
    |:--------:|:-------:|:--------:|:--------:|
    |   toto   |  wave 1 |  2014    |  300     |
    |   toto   |  wave 1 |  2015    |    0     |
    |   toto   |  wave 1 |  2016    |  450     |
    """
    if column not in df.columns:
        df[column] = nan

    if value is not None and column_value is not None:
        raise ValueError('You cannot set both the parameters value and column_value')

    if value is not None:
        df[column] = df[column].fillna(value)

    if column_value is not None:
        if column_value not in df.columns:
            raise ValueError(f'"{column_value}" is not a valid column name')
        df[column] = df[column].fillna(df[column_value])

    return df
