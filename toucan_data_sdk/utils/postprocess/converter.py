import logging

import pandas as pd

logger = logging.getLogger(__name__)


def convert_str_to_datetime(df, *, column=None, format=None):
    """
    Convert string column into datetime column
    :param df: Dataframe
    :param column: name of the column to format
    :param format: format of the values
    :return: df
    """
    df[column] = pd.to_datetime(df[column], format=format)
    return df


def convert_datetime_to_str(df, *, column=None, format=None):
    """
    Convert datetime column into string column
    :param df: Dataframe
    :param column: name of the column to format
    :param format: format of the result values
    :return: df
    """
    df[column] = df[column].dt.strftime(format)
    return df


def change_date_format(df, *, column, output_format, input_format=None, new_column=None):
    """
    Convert datetime column into string column
    :param df: Dataframe
    :param column: name of the column to format
    :param output_format: format of the output values
    :param input_format: format of the input values (If None, let the parser detect it)
    :param new_column: name of the output column
    :return: df
    """
    new_column = new_column or column
    df[new_column] = pd.to_datetime(df[column], format=input_format).dt.strftime(output_format)
    return df


def cast(df, column, type):
    """
    Convert column's type into type
    :param df: Dataframe
    :param column: name of the column to format
    :param type: desired type of the column
    :return: df
    """
    df[column] = df[column].astype(type)
    return df
