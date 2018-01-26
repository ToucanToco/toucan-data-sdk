import pandas as pd


def convert_str_to_datetime(df, selector, format=None):
    """
    Convert string column into datetime column
    :param df: Dataframe
    :param selector: name of the column to format
    :param format: format of the values
    :return: df
    """
    df[selector] = pd.to_datetime(df[selector], format=format)
    return df


def convert_datetime_to_str(df, selector, format):
    """
    Convert datetime column into string column
    :param df: Dataframe
    :param selector: name of the column to format
    :param format: format of the result values
    :return: df
    """
    df[selector] = df[selector].dt.strftime(format)
    return df
