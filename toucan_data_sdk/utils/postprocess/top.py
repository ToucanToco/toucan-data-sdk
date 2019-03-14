from typing import List, Union


def top(
        df,
        value: str,
        limit: int,
        order: str = 'asc',
        group: Union[str, List[str]] = None
):
    """
    Get the top or flop N results based on a column value for each specified group columns

    ---

    ### Parameters

    *mandatory :*
    - `value` (*str*): column name on which you will rank the results
    - `limit` (*int*): Number to specify the N results you want to retrieve.
        Use a positive number x to retrieve the first x results.
        Use a negative number -x to retrieve the last x results.

    *optional :*
    - `order` (*str*): `"asc"` or `"desc"` to sort by ascending ou descending order. By default : `"asc"`.
    - `group` (*str*, *list of str*): name(s) of columns on which you want to perform the group operation.

    ---

    ### Example

    **Input**

    | variable | Category | value |
    |:--------:|:--------:|:-----:|
    |   lili   |    1     |  50  |
    |   lili   |    1     |  20  |
    |   toto   |    1     |  100  |
    |   toto   |    1     |  200  |
    |   toto   |    1     |  300  |
    |   lala   |    1     |  100  |
    |   lala   |    1     |  150  |
    |   lala   |    1     |  250  |
    |   lala   |    2     |  350  |
    |   lala   |    2     |  450  |


    ```cson
    top:
      value: 'value'
      limit: 4
      order: 'asc'
    ```

    **Output**

    | variable | Category | value |
    |:--------:|:--------:|:-----:|
    |   lala   |    1     |  250  |
    |   toto   |    1     |  300  |
    |   lala   |    2     |  350  |
    |   lala   |    2     |  450  |
    """
    ascending = order != 'desc'
    limit = int(limit)
    filter_func = 'nlargest' if (limit > 0) ^ ascending else 'nsmallest'

    def _top(df):
        return getattr(df, filter_func)(abs(limit), value).sort_values(by=value,
                                                                       ascending=ascending)

    if group is None:
        df = _top(df)
    else:
        df = df.groupby(group).apply(_top)

    return df


def top_group(
        df,
        aggregate_by: List[str],
        value: str,
        limit: int,
        order: str = 'asc',
        function: str = 'sum',
        group: Union[str, List[str]] = None
):
    """
    Get the top or flop N results based on a function and a column value that agregates the input.
    The result is composed by all the original lines including only lines corresponding
    to the top groups

    ---

    ### Parameters

    *mandatory :*
    - `value` (*str*): Name of the column name on which you will rank the results.
    - `limit` (*int*): Number to specify the N results you want to retrieve from the sorted values.
        - Use a positive number x to retrieve the first x results.
        - Use a negative number -x to retrieve the last x results.
    - `aggregate_by` (*list of str*)): name(s) of columns you want to aggregate

    *optional :*
    - `order` (*str*): `"asc"` or `"desc"` to sort by ascending ou descending order. By default : `"asc"`.
    - `group` (*str*, *list of str*): name(s) of columns on which you want to perform the group operation.
    - `function` : Function to use to group over the group column

    ---

    ### Example

    **Input**

    | variable | Category | value |
    |:--------:|:--------:|:-----:|
    |   lili   |    1     |  50  |
    |   lili   |    1     |  20  |
    |   toto   |    1     |  100  |
    |   toto   |    1     |  200  |
    |   toto   |    1     |  300  |
    |   lala   |    1     |  100  |
    |   lala   |    1     |  150  |
    |   lala   |    1     |  250  |
    |   lala   |    2     |  350  |
    |   lala   |    2     |  450  |

    ```cson
    top_group:
      group: ["Category"]
      value: 'value'
      aggregate_by: ["variable"]
      limit: 2
      order: "desc"
    ```

    **Output**

    | variable | Category | value |
    |:--------:|:--------:|:-----:|
    |   toto   |    1     |  100  |
    |   toto   |    1     |  200  |
    |   toto   |    1     |  300  |
    |   lala   |    1     |  100  |
    |   lala   |    1     |  150  |
    |   lala   |    1     |  250  |
    |   lala   |    2     |  350  |
    |   lala   |    2     |  450  |
    """
    aggregate_by = aggregate_by or []
    group_top = group or []
    df2 = df.groupby(group_top + aggregate_by).agg(function).reset_index()
    df2 = top(df2, group=group, value=value, limit=limit, order=order).reset_index(drop=True)
    df2 = df2[group_top + aggregate_by]
    df = df2.merge(df, on=group_top + aggregate_by)

    return df
