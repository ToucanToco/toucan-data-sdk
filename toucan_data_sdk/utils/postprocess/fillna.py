def fillna(df, column, value):
    """
    Can fill NaN values from a column
    Args:
        df
        column
        value
    """
    if column in df.columns:
        df[column] = df[column].fillna(value)
    else:
        df[column] = value
    return df
