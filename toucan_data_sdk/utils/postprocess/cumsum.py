import logging

import pandas as pd


def cumsum(df, new_column: str, column: str, index: list, date_column: str, date_format: str):
    """
    DEPRECATED - please use `compute_cumsum` instead
    """
    logging.getLogger(__name__).warning('DEPRECATED: use compute_cumsum')
    date_temp = '__date_temp__'
    if isinstance(index, str):
        index = [index]
    levels = list(range(0, len(index)))
    df[date_temp] = pd.to_datetime(df[date_column], format=date_format)
    reference_cols = [date_temp, date_column]
    df = df.groupby(index + reference_cols).sum()
    df[new_column] = df.groupby(level=levels)[column].cumsum()
    df.reset_index(inplace=True)
    del df[date_temp]

    return df
