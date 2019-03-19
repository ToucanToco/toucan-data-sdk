from typing import List


def sort(df, columns: List[str], order='asc'):
    """

    Sort the data by the value in specified columns

    ---

    ### Parameters

    *mandatory :*
    - `columns` (*list*): list of the names of the columns to sort

    *optional :*
    - `order` (*str*): 'asc' (default) or 'desc'

    ---

    ### Example

    **Input**

    | variable | value |
    |:--------:|:-----:|
    |     A    |  220  |
    |     B    |  200  |
    |     C    |  300  |
    |     D    |  100  |

    ```cson
    sort:
      columns: ['variable']
      order: 'asc'
    ```

    **Output**

    | variable | value |
    |:--------:|:-----:|
    |     D    |  100  |
    |     B    |  200  |
    |     A    |  220  |
    |     C    |  300  |
    """
    ascending = order != 'desc'
    return df.sort_values(columns, ascending=ascending)
