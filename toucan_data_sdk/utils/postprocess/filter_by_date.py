"""date filtering helpers."""

import re
from calendar import monthrange
from datetime import date, datetime, timedelta
from uuid import uuid4

import pandas as pd

TIMEDELTA_RGX = re.compile(r'\s*(?P<num>\d+)\s*(?P<unit>\w+)$')


def _norm_date(datestr: str, date_fmt: str) -> date:
    """normalize symbolic date values (e.g. 'TODAY')

    Convert a symbolic value in a valid date.
    Currenlty known symbolic values are 'TODAY', 'YESTERDAY' and 'TOMORROW'.

    NOTE: This function will return `date` (not `datetime`) instances.

    Parameters:
        `datestr`: the date to parse, formatted as `date_fmt`
        `date_fmt`: expected output date format

    Returns:
        The interpreted date as a datetime.datetime object.
        If `datestr` doesn't match any of the known symbolic names, it just parses it.

    """
    try:
        days = {'TODAY': 0, 'YESTERDAY': -1, 'TOMORROW': 1}[datestr.upper()]
        return date.today() + pd.Timedelta(days=days)
    except KeyError:
        return datetime.strptime(datestr, date_fmt).date()


def add_offset(dateobj, hr_offset: str, sign: str):
    """add a human readable offset to `dateobj` and return corresponding date.

    rely on `pandas.Timedelta` and add the following extra shortcuts:
    - "w", "week" and "weeks" for a week (i.e. 7days)
    - "m", "month', "months" for a month (i.e. no day computation, just increment the month)
    - "y", "year", "years" for a year (i.e. no day computation, just increment the year)
    """
    sign_coeff = 1 if sign == '+' else -1
    try:
        return dateobj + sign_coeff * pd.Timedelta(hr_offset)
    except ValueError:
        # pd.Timedelta could not parse the offset, let's try harder
        match = TIMEDELTA_RGX.match(hr_offset)
        if match is not None:
            groups = match.groupdict()
            unit = groups['unit'].lower()[0]
            num = sign_coeff * int(groups['num'])
            # is it a week ?
            if unit == 'w':
                return dateobj + num * timedelta(weeks=1)
            # or a month ?
            if unit == 'm':
                return add_months(dateobj, num)
            # or a year ?
            if unit == 'y':
                return add_years(dateobj, num)
        # we did what we could, just re-raise the original exception
        raise


def add_months(dateobj, nb_months: int):
    """return `dateobj` + `nb_months`

    If landing date doesn't exist (e.g. february, 30th), return the last
    day of the landing month.

    >>> add_months(date(2018, 1, 1), 1)
    datetime.date(2018, 1, 1)
    >>> add_months(date(2018, 1, 1), -1)
    datetime.date(2017, 12, 1)
    >>> add_months(date(2018, 1, 1), 25)
    datetime.date(2020, 2, 1)
    >>> add_months(date(2018, 1, 1), -25)
    datetime.date(2015, 12, 1)
    >>> add_months(date(2018, 1, 31), 1)
    datetime.date(2018, 2, 28)
    """
    nb_years, nb_months = divmod(nb_months, 12)
    month = dateobj.month + nb_months
    if month > 12:
        nb_years += 1
        month -= 12
    year = dateobj.year + nb_years
    lastday = monthrange(year, month)[1]
    return dateobj.replace(year=year, month=month, day=min(lastday, dateobj.day))


def add_years(dateobj, nb_years):
    """return `dateobj` + `nb_years`

    If landing date doesn't exist (e.g. february, 30th), return the last
    day of the landing month.

    >>> add_years(date(2018, 1, 1), 1)
    datetime.date(2019, 1, 1)
    >>> add_years(date(2018, 1, 1), -1)
    datetime.date(2017, 1, 1)
    >>> add_years(date(2020, 2, 29), 1)
    datetime.date(2021, 2, 28)
    >>> add_years(date(2020, 2, 29), -1)
    datetime.date(2019, 2, 28)
    """
    year = dateobj.year + nb_years
    lastday = monthrange(year, dateobj.month)[1]
    return dateobj.replace(year=year, day=min(lastday, dateobj.day))


def parse_date(datestr: str, date_fmt: str) -> pd.Timestamp:
    """parse `datestr` and return corresponding date object.

    `datestr` should be a string matching `date_fmt` and parseable by `strptime`
    but some offset can also be added using `(datestr) + OFFSET` or `(datestr) -
    OFFSET` syntax. When using this syntax, `OFFSET` should be understable by
    `pandas.Timedelta` (cf.
    http://pandas.pydata.org/pandas-docs/stable/timedeltas.html) and `w`, `week`
    `month` and `year` offset keywords are also accepted. `datestr` MUST be wrapped
    with parenthesis.

    Additionally, the following symbolic names are supported: `TODAY`,
    `YESTERDAY`, `TOMORROW`.

    Example usage:

    >>> parse_date('2018-01-01', '%Y-%m-%d') datetime.date(2018, 1, 1)
    parse_date('(2018-01-01) + 1day', '%Y-%m-%d') datetime.date(2018, 1, 2)
    parse_date('(2018-01-01) + 2weeks', '%Y-%m-%d') datetime.date(2018, 1, 15)

    Parameters: `datestr`: the date to parse, formatted as `date_fmt`
        `date_fmt`: expected date format

    Returns: The `date` object. If date could not be parsed, a ValueError will
        be raised.
    """
    rgx = re.compile(r'\((?P<date>.*)\)(\s*(?P<sign>[+-])(?P<offset>.*))?$')
    datestr = datestr.strip()
    match = rgx.match(datestr)
    # if regexp doesn't match, date must match the expected format
    if match is None:
        dateobj = _norm_date(datestr, date_fmt)
    else:
        datestr = match.group('date').strip()
        dateobj = _norm_date(datestr, date_fmt)
        offset = match.group('offset')
        if offset:
            dateobj = add_offset(dateobj, offset, match.group('sign'))
    return pd.Timestamp(dateobj)


def filter_by_date(
    df,
    date_col: str,
    date_format: str = '%Y-%m-%d',
    start: str = None,
    stop: str = None,
    atdate: str = None,
):
    """
    Filter dataframe your data by date.

    This function will interpret `start`, `stop` and `atdate` and build
    the corresponding date range. The caller must specify either:

    - `atdate`: keep all rows matching this date exactly,
    - `start`: keep all rows matching this date onwards.
    - `stop`: keep all rows matching dates before this one.
    - `start` and `stop`: keep all rows between `start` and `stop`,

    Any other combination will raise an error. The lower bound of the date range
    will be included, the upper bound will be excluded.

    When specified, `start`, `stop` and `atdate` values are expected to match the
    `date_format` format or a known symbolic value (i.e. 'TODAY', 'YESTERDAY' or 'TOMORROW').

    Additionally, the offset syntax "(date) + offset" is also supported (Mind
    the parenthesis around the date string). In that case, the offset must be
    one of the syntax supported by `pandas.Timedelta` (see [pandas doc](
    http://pandas.pydata.org/pandas-docs/stable/timedeltas.html))

    ---

    ### Parameters

    *mandatory :*
    - `date_col` (*str*): the name of the dataframe's column to filter on

    *optional :*
    - `date_format` (*str*): expected date format in column `date_col` (see [available formats](
    https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior)
    - `start` (*str*): if specified, lower bound (included) of the date range
    - `stop` (*str*): if specified, upper bound (excluded) of the date range
    - `atdate` (*str*): if specified, the exact date we're filtering on
    """
    mask = None
    if start is None and stop is None and atdate is None:
        raise TypeError('either "start", "stop" or "atdate" must be specified')
    if start is not None and atdate is not None:
        raise TypeError('"start" and "atdate" are mutually exclusive')
    if stop is not None and atdate is not None:
        raise TypeError('"stop" and "atdate" are mutually exclusive')
    # add a new column that will hold actual date objects instead of strings.
    # This column is just temporary and will be removed before returning the
    # filtered dataframe.
    filtercol = str(uuid4())
    df[filtercol] = pd.to_datetime(df[date_col], format=date_format)
    if atdate is not None:
        mask = df[filtercol] == parse_date(atdate, date_format)
    elif start is not None and stop is not None:
        mask = (df[filtercol] >= parse_date(start, date_format)) & (
            df[filtercol] < parse_date(stop, date_format)
        )
    # atdate is None and start or stop is None
    elif start is not None and stop is None:
        mask = df[filtercol] >= parse_date(start, date_format)
    elif stop is not None and start is None:
        mask = df[filtercol] < parse_date(stop, date_format)
    return df[mask].drop(filtercol, axis=1)
