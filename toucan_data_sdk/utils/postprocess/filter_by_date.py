"""date filtering helpers."""

from uuid import uuid4
from datetime import date, datetime

import pandas as pd


def _norm_date(datestr: str, date_fmt: str):
    """normalize symbolic date values (e.g. 'TODAY')

    Convert a symbolic value in a valid date, formatted as `date_fmt`.
    Currenlty known symbolic values are 'TODAY', 'YESTERDAY' and 'TOMORROW'.


    Parameters:
        `datestr`: the date to parse
        `date_fmt`: expected output date format

    Returns:
        The interpreted date as a string. If `datestr` doesn't match any of the
        known symbolic names, it is left untouched.

    """
    try:
        days = {'TODAY': 0, 'YESTERDAY': -1, 'TOMORROW': 1}[datestr.upper()]
        return date.today() + pd.Timedelta(days=days)
    except KeyError:
        return datetime.strptime(datestr, date_fmt)


def filter_by_date(df, date_col, date_fmt='%Y-%m-%d', start=None, stop=None, delta=None):
    """filter dataframe `df` by date.

    This function will interpret `start`, `stop` and `delta` and build
    the corresponding date range. The caller must specify either:

    - `start`: keep all rows matching this date exactly,
    - `start` and `stop`: keep all rows between `start` and `stop`,
    - `start` and `delta`: keep all rows between `start` and `start` + `delta`,
    - `stop` and `delta`: keep all rows between `stop` - `delta` and `start`.

    Any other combination will raise an error. The lower bound of the date range
    will be included, the upper bound will be excluded.

    When specified, `start` and `stop` values are expected to match the
    `date_fmt` format or to be a known symbolic value (i.e. 'TODAY',
    'YESTERDAY' or 'TOMORROW').

    Parameters:
        `df`: the dataframe to filter
        `date_col`: the name of the dataframe's column to filter on
        `date_fmt`: expected date format in column `date_col`
        `start`: if specified, lower bound (included) of the date range
        `stop`: if specified, upper bound (excluded) of the date range
        `delta`: if specified, date range span. The value must be a string
            understable by `pandas.Timedelta` (cf.
            http://pandas.pydata.org/pandas-docs/stable/timedeltas.html)

    Returns:
        The filtered dataframe
    """
    mask = None
    if start is None and stop is None:
        raise TypeError('either "start" or "stop" must be specified')
    # add a new column that will hold actual date objects instead of strings.
    # This column is just temporary and will be removed before returning the
    # filtered dataframe.
    filtercol = str(uuid4())
    df[filtercol] = pd.to_datetime(df[date_col], format=date_fmt)
    if start is not None and stop is not None:
        if delta is not None:
            raise TypeError('if "start" and "stop" are specified, "delta" must be None')
        mask = ((df[filtercol] >= _norm_date(start, date_fmt)) &
                (df[filtercol] < _norm_date(stop, date_fmt)))
    elif stop is None:
        start = _norm_date(start, date_fmt)
        if delta is None:
            mask = df[filtercol] == start
        else:
            stop = start + pd.Timedelta(delta)
            mask = (df[filtercol] >= start) & (df[filtercol] < stop)
    elif start is None:
        if delta is None:
            raise TypeError(
                '"stop" without "start" nor "delta" is forbidden, use "start" instead')
        stop = _norm_date(stop, date_fmt)
        start = stop - pd.Timedelta(delta)
        mask = (df[filtercol] >= start) & (df[filtercol] < stop)
    return df.loc[mask].drop(filtercol, axis=1)
