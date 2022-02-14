from typing import Any, Dict, Optional

import pandas as pd

from ..helpers import setlocale


def date_requester_generator(
    df: pd.DataFrame,
    date_column: str,
    frequency: str,
    date_column_format: Optional[str] = None,
    format: str = "%Y-%m-%d",
    granularities: Optional[Dict[str, str]] = None,
    others_format: Optional[Dict[str, str]] = None,
    times_delta: Optional[Dict[str, str]] = None,
    locale: Optional[str] = None,
) -> pd.DataFrame:
    """
    From a dataset containing dates in a column, return a dataset
    with at least 3 columns :
    - "DATE" : Label of date
    - "DATETIME" : Date in datetime dtype
    - "GRANULARITY" : Granularity of date

    ---

    ### Parameters

    *mandatory :*
    - `date_column` (*str*): name of column containing the date in the dataframe
    - `frequency` (*str*): see [pandas doc](
    http://pandas.pydata.org/pandas-docs/stable/timeseries.html#offset-aliases)

    *optional :*
    - `date_column_format` (*str*): format of the date in date_column
    - `format` (*str*): format of the date (see [pandas doc](
        https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior))
        By default, the format is set to `'%d/%m/%Y'`
        **WARNING**: only use if `granularities` is None.
    - `granularities` (*dict*):
        - key (*str*): name of the granularity
        - value (*str*): Format of the granularity e.g. '%d/%m/%Y' (see [pandas doc](
            https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior))
    - `others_format` (*dict*): Add new columns for each key
        - key (*str*): name of the column
        - value (*str*): format of the granularity e.g. '%d/%m/%Y' (see [pandas doc](
            https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior))
    - `times_delta` (*dict*): Add new columns for each key
        - key (*str*): name of the column
        - value (*str*): time delta (e.g. '+1 day', '+3 day', '-4 month')
    - `locale` (*str*): locale used to display the dates (by default, the process one is taken)
    ---

    ### Example

    **Input**

    date | kpi
    :---:|:-----:
    2018-01-01 | 1
    2018-01-05 | 2
    2018-01-04 | 3
    2018-01-03 | 4
    2018-01-02 | 5

    ```cson
    date_requester_generator:
      date_column: 'date'
      frequency: 'D'
      granularities:
        'day': '%d/%m/%Y'
        'Semaine': '%W'
      others_format:
        'year': '%Y'
    ```

    **Ouput**

    DATE  |  DATETIME  | GRANULARITY | year
    :---------:|:----------:|:-----------:|:---:
    01/01/2018 | 2018-01-01 |         day | 2018
    02/01/2018 | 2018-01-02 |         day | 2018
    03/01/2018 | 2018-01-03 |         day | 2018
    04/01/2018 | 2018-01-04 |         day | 2018
    05/01/2018 | 2018-01-05 |         day | 2018
    01 | 2018-01-01 |     Semaine | 2018
    """
    with setlocale(locale):
        start_date = pd.to_datetime(df[date_column], format=date_column_format).min()
        end_date = pd.to_datetime(df[date_column], format=date_column_format).max()

        granularities = granularities or {"date": format}
        others_format = others_format or {}
        times_delta = times_delta or {}

        # Base DataFrame
        columns_list = ["DATE", "DATETIME", "GRANULARITY", *others_format, *times_delta]
        result_df: Dict[str, Any] = {col_name: [] for col_name in columns_list}

        # Generate the range
        date_range = pd.date_range(start=start_date, end=end_date, freq=frequency)

        for granularity_name, granularity_format in granularities.items():
            date_range_label = date_range.strftime(granularity_format)
            date_range_label_as_list = list(date_range_label)
            first_index = list(set([date_range_label_as_list.index(x) for x in date_range_label]))
            date_range_datetime = date_range[first_index]
            date_range_label = date_range_label.unique()

            result_df["DATE"] += list(date_range_label)
            result_df["DATETIME"] += list(date_range_datetime)
            result_df["GRANULARITY"] += [granularity_name] * len(date_range_label)

            for col_name, other_format in others_format.items():
                result_df[col_name] += list(date_range_datetime.strftime(other_format))

            for col_name, time_delta in times_delta.items():
                result_df[col_name] += list(
                    (date_range_datetime + pd.Timedelta(time_delta)).strftime(granularity_format)
                )

    return pd.DataFrame(result_df)
