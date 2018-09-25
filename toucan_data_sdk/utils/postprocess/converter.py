import logging
from functools import wraps

import pandas as pd

logger = logging.getLogger(__name__)


def handle_deprecated(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'selector' in kwargs:
            logger.warning('The parameter `selector` is deprecated. '
                           'Please switch the name to `column`.')
            selector = kwargs.pop('selector')
            kwargs['column'] = kwargs.get('column', selector)
        return f(*args, **kwargs)

    return wrapper


@handle_deprecated
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


@handle_deprecated
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
