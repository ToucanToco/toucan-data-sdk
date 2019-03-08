import pandas as pd
import logging


def cumsum(df, new_column: str, column: str, index: list, date_column: str, date_format: str):
    """
    DEPRECATED
    Creates a new column, which is the cumsum of the column

    - new_column: name of the created column
    - column: name on which the cumulative sum is performed
    - index: list of column names to keep as indices
    - date_column: column name that represent the date
    - date_format: format of the date
    List of available format:
    https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
    """
    logging.getLogger(__name__).warning(f"DEPRECATED: use compute_cumsum")
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
