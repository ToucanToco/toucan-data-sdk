def argmax(df, column:str):
    """
    Keep the row of the data corresponding to the maximal value in a column

    - column: name of the column containing the value you want to keep the maximum
    """
    df = df[df[column] == df[column].max()]
    return df


def argmin(df, column:str):
    """
    Keep the row of the data corresponding to the minimal value in a column

    - column: name of the column containing the value you want to keep the minimum
    """
    df = df[df[column] == df[column].min()]
    return df
