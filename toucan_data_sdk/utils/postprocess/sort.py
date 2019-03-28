from typing import List, Union


def sort(df, columns: Union[str, List[str]], order: Union[str, List[str]] = None):
    """

    Sort the data by the value in specified columns

    ---

    ### Parameters

    *mandatory :*
    - `columns` (*list*): dict of the column names as keys and order
    ('asc' or 'desc') as values.

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
      columns:
       'variable': 'asc'
    ```

    **Output**

    | variable | value |
    |:--------:|:-----:|
    |     D    |  100  |
    |     B    |  200  |
    |     A    |  220  |
    |     C    |  300  |

    """
    if not isinstance(columns, list):
        columns = [columns]
    if order is None:
        orders = ['asc'] * len(columns)
    else:
        if not isinstance(order, list):
            order = [order]
        assert len(order) == len(columns), "'columns' and 'order' lists" \
                                           "must be of same length"
        orders = []
        for ord in order:
            assert ord in ['asc', 'desc'], f"Got order value: {order}." \
                                            "Expected 'asc' or 'desc'"
            orders.append(ord == 'asc')
        print(orders)
    return df.sort_values(columns, ascending=orders)
