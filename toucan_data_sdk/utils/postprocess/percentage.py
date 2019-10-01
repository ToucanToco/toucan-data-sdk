from typing import List, Union


def percentage(df, column: str, group_cols: Union[str, List[str]] = None, new_column: str = None):
    """
    Add a column to the dataframe according to the groupby logic on group_cols

    ---

    ### Parameters

    *mandatory :*
    - `column` (*str*): name of the desired column you need percentage on

    *optional :*
    - `group_cols` (*list*): names of columns for the groupby logic
    - `new_column` (*str*): name of the output column. By default `column` will be overwritten.

    ---

    **Input**

    | gender |    sport   | number |
    |:------:|:----------:|:------:|
    |  male  |   bicycle  |   17   |
    | female | basketball |   17   |
    |  male  | basketball |    3   |
    | female |  football  |    7   |
    | female |   running  |   30   |
    |  male  |   running  |   20   |
    |  male  |  football  |   21   |
    | female |   bicycle  |   17   |

    ```cson
    percentage:
      new_column: 'number_percentage'
      column: 'number'
      group_cols: ['sport']
    ```

    **Output**

    | gender |    sport   | number | number_percentage |
    |:------:|:----------:|:------:|:-----------------:|
    |  male  |   bicycle  |   17   |        50.0       |
    | female | basketball |   17   |        85.0       |
    |  male  | basketball |    3   |        15.0       |
    | female |  football  |    7   |        25.0       |
    | female |   running  |   30   |        60.0       |
    |  male  |   running  |   20   |        40.0       |
    |  male  |  football  |   21   |        75.0       |
    | female |   bicycle  |   17   |        50.0       |
    """
    new_column = new_column or column
    if group_cols is None:
        df[new_column] = 100.0 * df[column] / sum(df[column])
    else:
        df[new_column] = 100.0 * df[column] / df.groupby(group_cols)[column].transform(sum)
    return df
