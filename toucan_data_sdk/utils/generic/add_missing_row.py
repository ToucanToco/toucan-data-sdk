from typing import Dict, List, Union

import pandas as pd

from toucan_data_sdk.utils.helpers import (
    check_params_columns_duplicate,
    ParamsValueError
)


def add_missing_row(
    df: pd.DataFrame,
    id_cols: List[str],
    reference_col: str,
    complete_index: Union[Dict[str, str], List[str]] = None,
    method: str = None,
    cols_to_keep: List[str] = None
) -> pd.DataFrame:
    """
    Add missing row to a df base on a reference column

    ---

    ### Parameters

    *mandatory :*
    - `id_cols` (*list of str*): names of the columns used to create each group
    - `reference_col` (*str*): name of the column used to identify missing rows

    *optional :*
    - `complete_index` (*list* or *dict*): [A, B, C] a list of values used to add missing rows.
      It can also be a dict to declare a date range.
      By default, use all values of reference_col.
    - `method` (*str*): by default all missing rows are added. The possible values are :
        - `"between"` : add missing rows having their value between min and max values for each group,
        - `"between_and_after"` : add missing rows having their value bigger than min value for each group.
        - `"between_and_before"` : add missing rows having their value smaller than max values for each group.
    - `cols_to_keep` (*list of str*): name of other columns to keep, linked to the reference_col.

    ---

    ### Example

    **Input**

    YEAR | MONTH | NAME
    :---:|:---:|:--:
    2017|1|A
    2017|2|A
    2017|3|A
    2017|1|B
    2017|3|B

    ```cson
    add_missing_row:
      id_cols: ['NAME']
      reference_col: 'MONTH'
    ```

    **Output**

    YEAR | MONTH | NAME
    :---:|:---:|:--:
    2017|1|A
    2017|2|A
    2017|3|A
    2017|1|B
    2017|2|B
    2017|3|B

    """
    if cols_to_keep is None:
        cols_for_index = [reference_col]
    else:
        cols_for_index = [reference_col] + cols_to_keep
    check_params_columns_duplicate(id_cols + cols_for_index)

    if method == 'between' or method == 'between_and_after':
        df['start'] = df.groupby(id_cols)[reference_col].transform(min)
        id_cols += ['start']
    if method == 'between' or method == 'between_and_before':
        df['end'] = df.groupby(id_cols)[reference_col].transform(max)
        id_cols += ['end']

    names = id_cols + cols_for_index
    new_df = df.set_index(names)
    index_values = df.groupby(id_cols).sum().index.values

    if complete_index is None:
        complete_index = df.groupby(cols_for_index).sum().index.values
    elif isinstance(complete_index, dict):
        if complete_index['type'] == 'date':
            freq = complete_index['freq']
            date_format = complete_index['format']
            start = complete_index['start']
            end = complete_index['end']
            if isinstance(freq, dict):
                freq = pd.DateOffset(**{k: int(v) for k, v in freq.items()})
            complete_index = pd.date_range(start=start, end=end, freq=freq)
            complete_index = complete_index.strftime(date_format)
        else:
            raise ParamsValueError(f'Unknown complete index type: '
                                   f'{complete_index["type"]}')

    if not isinstance(index_values[0], tuple):
        index_values = [(x,) for x in index_values]
    if not isinstance(complete_index[0], tuple):
        complete_index = [(x,) for x in complete_index]
    new_tuples_index = [x + y for x in index_values for y in complete_index]

    new_index = pd.MultiIndex.from_tuples(new_tuples_index, names=names)
    new_df = new_df.reindex(new_index).reset_index()

    if method == 'between' or method == 'between_and_after':
        new_df = new_df[new_df[reference_col] >= new_df['start']]
        del new_df['start']
    if method == 'between' or method == 'between_and_before':
        new_df = new_df[new_df[reference_col] <= new_df['end']]
        del new_df['end']

    return new_df
