
def round_values(df, params):
    """
    This function replace numeric column values inplace by the rounded value.

    :param df: the dataframe to which we want to apply the round function
    :param kwargs: a dictionary with:
      - key: column name to which we want to apply the round function
      - value: Number of decimal places to round the column to
    :return: the df dataframe with the rounded value columns.


    Examples:

    Dataset df:

    ENTITY  VALUE_1  VALUE_2
       A     -1.5     -1.5
       A      0.4      0.4
       A       0        0
       A      1.6      1.6

    rank(df, params={'VALUE_1': None, 'VALUE_2': 1}) returns:

    ENTITY  VALUE_1  VALUE_2
       A     -2.0     -1.6
       A      0.0      0.4
       A      0.0      0.0
       A      2.0      1.6

    """

    for column, decimal in params.items():
        df[column] = df[column].round(decimal)
    return df
