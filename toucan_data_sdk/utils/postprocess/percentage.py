def percentage(df, new_column, column, group_cols=None):
    """
    Add a column to the dataframe according to the groupby logic on group_cols
    :param df: Dataframe
    :param new_column: name of the new column
    :param column: name of the desired column you need percentage on
    :param group_cols: (str | list of str) or None
    :return: df + the percentage column
    """
    if group_cols is None:
        df[new_column] = 100. * df[column] / sum(df[column])
    else:
        df[new_column] = 100. * df[column] / df.groupby(group_cols)[column].transform(sum)
    return df
