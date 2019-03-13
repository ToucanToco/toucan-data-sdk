import pandas as pd


def date_requester_generator(df, date_column, frequency, date_column_format=None,
                             format='%Y-%m-%d', granularities=None,
                             others_format=None, times_delta=None):
    """
    **From a dataframe containing dates in a column, return a dataframe**
    **with at least 3 columns :**
    **- "DATE" : Label of date**
    **- "DATETIME" : Date in datetime dtype**
    **- "GRANULARITY" : Granualrity of date**

    - `date_column` (str): name of column containing the date in the dataframe
    - `frequency` (str) : see [pandas doc](
    http://pandas.pydata.org/pandas-docs/stable/timeseries.html#offset-aliases)
    - `date_column_format` (optional: str): format of the date in date_column
    - `format` (optional: str): format of the date. !!! only use if granularity is None.
        NB : same format in Toucan Toco
        _Example : '%d/%m/%Y'_ (see [pandas doc](
        https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior))
    - `granularities` (optional: dict):
        - keys : name of the granularity
        - values (str): Format of the granularity.
            NB : same format in Toucan Toco
            _Example : '%d/%m/%Y'_ (see [pandas doc](
            https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior))
    - `others_format` (optional: dict) : Add new columns for each key
        - key (str) : name of the column
        - values (str): format of the granularity.
            NB : same format in Toucan Toco
            _Example : '%d/%m/%Y'_ (see [pandas doc](
            https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior))

    - `times_delta` (optional: dict) : Add new columns for each key
        - key (str) : name of the column
        - values (str): time delta
            _Examples : '+1 day', '+3 day', '-4 month'_
    """

    start_date = pd.to_datetime(df[date_column], format=date_column_format).min()
    end_date = pd.to_datetime(df[date_column], format=date_column_format).max()

    granularities = granularities or {'date': format}
    others_format = others_format or {}
    times_delta = times_delta or {}

    # Base DataFrame
    columns_list = ['DATE', 'DATETIME', 'GRANULARITY', *others_format, *times_delta]
    result_df = {col_name: [] for col_name in columns_list}

    # Generate the range
    date_range = pd.date_range(start=start_date, end=end_date, freq=frequency)

    for granularity_name, granularity_format in granularities.items():
        date_range_label = date_range.strftime(granularity_format)
        a = list(set(date_range_label))
        index_unique = list(set([a.index(x) for x in date_range_label]))
        date_range_datetime = date_range[index_unique]
        date_range_label = date_range_label.unique()

        result_df['DATE'] += list(date_range_label)
        result_df['DATETIME'] += list(date_range_datetime)
        result_df['GRANULARITY'] += [granularity_name] * len(date_range_label)

        for col_name, other_format in others_format.items():
            result_df[col_name] += list(date_range_datetime.strftime(other_format))

        for col_name, time_delta in times_delta.items():
            result_df[col_name] += list((date_range_datetime + pd.Timedelta(time_delta))
                                        .strftime(granularity_format))

    return pd.DataFrame(result_df)
