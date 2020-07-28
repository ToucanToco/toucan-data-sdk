from typing import List, Optional
from uuid import uuid4

import pandas as pd

from .filter_by_date import parse_date


def categories_from_dates(
    df,
    date_col: str,
    new_column: str,
    range_steps: List[str],
    category_names: Optional[List[str]] = None,
    date_format: str = '%Y-%m-%d',
):
    """
    Create a new column of categories based on a date column.
    This function will gather into categories dates from the date column
    based on range steps.

    For instance, the dates: [2018-01-02, 2018-01-06, 2018-01-15, 2018-01-16, 2018-01-20]
    with the steps: [2018-01-07, 2018-01-18] will give 3 categories:
    - First category: [2018-01-02, 2018-01-06]
    - Second category: [2018-01-15, 2018-01-16]
    - Third category: [2018-01-20]

    ### Parameters

    *mandatory :*
    - `date_col` (*str*): name of the date column
    - `new_column` (*str*): name of the column for created categories
    - `range_steps` (*list* of *str*): a list of valid dates.
    Each date should be a string matching `date_fmt` and parsable by `strptime`
    but some offset can also be added using `(datestr) + OFFSET` or `(datestr) - OFFSET` syntax.
    When using this syntax, `OFFSET` should be understable by `pandas.Timedelta`
    (see http://pandas.pydata.org/pandas-docs/stable/timedeltas.html)
    and `w`, `week`, `month` and `year` offset keywords are also accepted.
    Additionally, the following symbolic names are supported: `TODAY`, `YESTERDAY`, `TOMORROW`.
    _NOTE_: `datestr` **MUST** be wrapped with parenthesis.

    *optional :*
    - `category_names` (*list* of *str*): names of the categories to be created.
    This list must have a length equal to `range_step` **plus one**
    - `date_format` (*str*): expected date format in column `date_col` (see [available formats](
    https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior)

    ### Example:

    **Input**

    |    date      |    value   |
    |:------------:|:----------:|
    |  2018-01-28  |      1     |
    |  2018-01-28  |      2     |
    |  2018-01-29  |      3     |
    |  2018-01-30  |      1     |
    |  2018-02-01  |      6     |
    |  2019-01-05  |      7     |
    |  2019-01-06  |      7     |
    |  2019-01-07  |      1     |
    |  2019-01-04  |      1     |

    ```cson
    categories_from_dates:
      date_col: 'date'
      new_column: 'categories'
      range_steps: ['(TODAY)-10days', '(TODAY)+1days']
      category_names: ['Old', 'Recent', 'Futur']
    ```

    **Output**

    *Assuming today is 2019-01-06*

    |    date      |    value   | categories |
    |:------------:|:----------:|:----------:|
    |  2018-01-28  |      1     |    Old     |
    |  2018-01-28  |      2     |    Old     |
    |  2018-01-29  |      3     |    Old     |
    |  2018-01-30  |      1     |    Old     |
    |  2018-02-01  |      6     |    Old     |
    |  2019-01-05  |      7     |   Recent   |
    |  2019-01-06  |      7     |   Futur    |
    |  2019-01-07  |      1     |   Futur    |
    |  2019-01-04  |      1     |   Recent   |
    """

    category_names = category_names or [f'Category {i+1}' for i in range(len(range_steps) + 1)]
    if len(range_steps) == 0:
        raise TypeError('range_steps should not have length 0')
    if len(range_steps) + 1 != len(category_names):
        raise TypeError('category_names should have length len(range_steps)+1')

    date_col_at_date_format = str(uuid4())
    df[date_col_at_date_format] = pd.to_datetime(df[date_col], format=date_format)
    df[new_column] = ''

    # first category
    df[new_column][
        df[date_col_at_date_format] < parse_date(range_steps[0], date_format)
    ] = category_names[0]

    # second to before last category
    for i in range(len(range_steps[:-1])):
        start = range_steps[i]
        stop = range_steps[i + 1]
        mask = (df[date_col_at_date_format] < parse_date(stop, date_format)) & (
            df[date_col_at_date_format] >= parse_date(start, date_format)
        )
        df[new_column][mask] = category_names[i + 1]

    # last category
    df[new_column][
        df[date_col_at_date_format] >= parse_date(range_steps[-1], date_format)
    ] = category_names[-1]

    return df.drop(columns=date_col_at_date_format)
