def replace(df, column: str, new_column: str = None, **kwargs):
    """
    Replace values of a column
    ---
    - `column` (str): name of the column containing values to replace
    - `new_column` (optional: str): name of the column which will contain replaced
        if 'None' column' will be overwritten
    """
    new_column = new_column or column
    df.loc[:, new_column] = df[column].replace(**kwargs)
    return df
