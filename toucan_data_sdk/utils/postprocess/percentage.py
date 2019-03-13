from typing import Union, List


def percentage(df, column, group_cols: Union[str, List[str]] = None, new_column: str = None):
    """
    Add a column to the dataframe according to the groupby logic on group_cols
    ---
    - `column` (str): name of the desired column you need percentage on
    - `new_column` (optional : str): name of the new column
    - `group_cols` (list): list of columns on which compute the percentage
    """
    new_column = new_column or column
    if group_cols is None:
        df[new_column] = 100. * df[column] / sum(df[column])
    else:
        df[new_column] = 100. * df[column] / df.groupby(group_cols)[column].transform(sum)
    return df
