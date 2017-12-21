import pandas as pd

from toucan_data_sdk.utils.helpers import check_params_columns_duplicate


def add_missing_row(df, id_cols, reference_col, complete_index=None, method=None, keep_cols=None):
    """
    Add missing row to a df base on a reference column
    - `id_cols` are the columns id to group,
    - `reference_col` is the column with groups missing values
    - `complete_index` (optional) a set of values used to add missing rows,
       by default use the function `unique` on reference_col
    - `method` (optional) method to choose values to keep.
       E.g between min and max value of the group.
    - `keep_cols` (optional) is the columns link to the reference_col to keep.

    For example :

    YEAR MONTH NAME  VALUE  X
    2017   1     A      1  lo
    2017   2     A      1  lo
    2017   3     A      1  la
    2017   1     B      1  la
    2017   3     B      1  la

    The function `add_missing_row` with the arguments :
            id_cols=['NAME']
            reference_col='MONTH'
    give as a result :


    YEAR MONTH NAME  VALUE  X
    2017   1     A      1  lo
    2017   2     A      1  lo
    2017   3     A      1  la
    2017   1     B      1  la
    2017   2     B      NA NA
    2017   3     B      1  la

    Args:
        df (pd.DataFrame):
        id_cols (list(str)):
        reference_col (str):
        complete_index (tuple):
        method (str):
        keep_cols (list(str)):
    """
    if keep_cols is None:
        cols_for_index = [reference_col]
    else:
        cols_for_index = [reference_col] + keep_cols
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
