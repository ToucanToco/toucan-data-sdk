from typing import List, Optional


def drop_duplicates(df, columns: Optional[List[str]]):
    """
    Remove duplicate rows

    ---

    ### Parameters

    *mandatory :*
    - `columns` (*list*): columns to consider to identify duplicates (set to null to use all the columns)

    ### Example

    **Input**

    | name | country | year |
    |:----:|:-------:|:----:|
    | toto |  France | 2014 |
    | titi | England | 2015 |
    | toto |  France | 2014 |
    | toto |  France | 2016 |


    ```cson
    drop_duplicates:
      columns: null
    ```

    **Output**

    | name | country | year |
    |:----:|:-------:|:----:|
    | toto |  France | 2014 |
    | titi | England | 2015 |
    | toto |  France | 2016 |
    """
    return df.drop_duplicates(columns)


def query(df, query):
    """
    Filter a dataset under a condition

    ---

    ### Parameters

    *mandatory :*
    - query (*str*): your query as a string (see [pandas doc](
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
