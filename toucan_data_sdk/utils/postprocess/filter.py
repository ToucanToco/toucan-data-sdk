from typing import List


def drop_duplicates(df, columns: List[str]):
    """
    Drop duplicated rows
    ---
    - `columns` (optional: list): list of column name to identify duplicates, if 'None' all columns are used  # noqa E501
    """
    return df.drop_duplicates(columns)


def query(df, query):
    """
    Filter a dataset under a condition

    ---

    ### Parameters

    - query (str): your query as a string (see [pandas doc](
    http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.query.html#pandas.DataFrame.query))

    ---

    ### Example

    **Input**

    | variable |   wave  |  year    | value |
    |:--------:|:-------:|:--------:|:-----:|
    |   toto   |  wave 1 |  2014    |  300  |
    |   toto   |  wave 1 |  2015    |  250  |
    |   toto   |  wave 1 |  2015    |  100  |
    |   toto   |  wave 1 |  2016    |  450  |


    ```cson
    query: 'value > 350'
    ```

    **Output**

    | variable |   wave  |  year    | value |
    |:--------:|:-------:|:--------:|:-----:|
    |   toto   |  wave 1 |  2016    |  450  |
    """
    df = df.query(query)
    return df
