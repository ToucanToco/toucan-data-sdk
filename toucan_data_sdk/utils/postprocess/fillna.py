from numpy import nan


def fillna(df, column: str, value=None,  column_value=None):
    """
    Can fill NaN values from a column - you can fill with column or with value

    - column: name of column you want to fill
    - value(optional): NaN will be replaced by this value
    - column_value(optional): NaN will be replaced by value from this column
    NB: You must set either the 'value' parameter or the 'column_value' parameter
    """
    if column not in df.columns:
        df[column] = nan

    if value is not None and column_value is not None:
        raise ValueError('You cannot set both the 'value' parameter and 'column_value' parameter)

    if value is not None:
        df[column] = df[column].fillna(value)

    if column_value is not None:
        if column_value not in df.columns:
            raise ValueError(f'"{column_value}" is not a valid column name')
        df[column] = df[column].fillna(df[column_value])

    return df
