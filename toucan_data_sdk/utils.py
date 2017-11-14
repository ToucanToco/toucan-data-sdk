"""
Contains a series of reusable functions for the data pipeline

TODO: to start filling and organize later
"""
from __future__ import unicode_literals

import logging

import pandas as pd


def roll_up(df, levels, groupby_vars, extra_groupby_cols=None,
            var_name='type', value_name='value', agg_func='sum'):
    """
    Move the hierarchy from the columns name to the rows (like a melt).
    Add higher level hierarchy information with pandas aggregation function.

    One DatFrame per level (all will be concatenated in the end), group by
    levels, apply aggregation function on groupby_vars. Add two extra columns:
    value_name and var_name, like a pandas melt.

    Args:
        df (DataFrame): DataFrame to work on...
        levels (list): Hierarchy. The order is important, from the top level
            to the lower level.
        groupby_vars (list): Columns to select from the group by (apply
            aggregation function to)
        extra_groupby_cols (list): Add to columns to group by each time.
        var_name (str): Same as a pandas melt() var_name
        value_name (str): Same as a pandas melt() value_name
        agg_func (str): pandas aggregation function to apply to the groupby.

    Returns:
        DataFrame:

    """
    if extra_groupby_cols is None:
        extra_groupby_cols = []
    dfs = []
    groupby_cols_cpy = list(levels)
    levels_cpy = list(levels)
    levels_cpy.reverse()
    for top_level in levels_cpy:
        # Aggregation
        gb_df = getattr(df.groupby(groupby_cols_cpy + extra_groupby_cols)
                        [groupby_vars], agg_func)().reset_index()

        # Melt-like columns
        gb_df[var_name] = top_level
        gb_df[value_name] = gb_df[top_level]
        dfs.append(gb_df)

        # Remove one level each time in the groupby: lowest level column needs
        # a groupby with every levels, the next level needs every one except
        # the lowest, etc. until the top level column that needs only itself
        # inside the groupby.
        groupby_cols_cpy.pop()
    return pd.concat(dfs).reset_index()


def two_values_melt(df, first_value_vars, second_value_vars,
                    var_name, value_name):
    """
    First, build two DataFrames from the original one: one to compute a melt
    for the value, another one to compute a melt for the evolution. Second,
    merge these two DataFrames. The idea is to go from something like this:

    | ... | <some1> | <some2> | <some1_evol> | <some2_evol> |
    | ... | <val1>  | <val2>  | <evol1>      | <evol2>      |

    to something like that:

    | ... | variable  | value  | evolution
    | ... | --------- | ------ | ---------
    | ... |  <some1>  | <val1> | <evol1>
    | ... |  <some2>  | <val2> | <evol2>

    Args:
        df (DataFrame): DataFrame to process
        first_value_vars (list): value_vars of a pandas melt, for the first
            value columns of the DataFrame
        second_value_vars (list): value_vars of a pandas melt, for the second
            value columns of the DataFrame
        var_name (str): var_names of a pandas melt
        value_name (str): value_name of a pandas melt

    Notes:
        In tests/app/fixtures, you will find example files for the input and
        output data (respectively two_values_melt_in.csv and
        two_values_melt_out.csv)

    Returns:
        DataFrame: molted DataFrame with two value (value and evolution for
            example) columns

    """
    value_name_first = value_name + '_first'
    value_name_second = value_name + '_second'

    # Melt on the first value columns
    melt_first_value = pd.melt(df,
                               id_vars=[col for col in list(
                                   df) if col not in first_value_vars],
                               value_vars=first_value_vars,
                               var_name=var_name,
                               value_name=value_name_first)
    melt_first_value.drop(second_value_vars, axis=1, inplace=True)

    # Melt on the second value columns
    melt_second_value = pd.melt(df,
                                id_vars=[col for col in list(
                                    df) if col not in second_value_vars],
                                value_vars=second_value_vars,
                                var_name=var_name,
                                value_name=value_name_second)

    # Since there are two value columns, there is no need to keep the
    # second_value_vars names. And it will make things easier for the merge.
    normalize_types = dict(list(zip(second_value_vars, first_value_vars)))
    melt_second_value.replace(normalize_types, inplace=True)
    melt_second_value.drop(first_value_vars, axis=1, inplace=True)

    on_cols = list(melt_first_value)
    on_cols.remove(value_name_first)
    return pd.merge(
        melt_first_value, melt_second_value, on=on_cols, how='outer'
    )


def compute_evolution(
        df,
        id_cols,
        date_col,
        value_col,
        freq=1,
        method='abs',
        format='column',
        offseted_suffix='_offseted',
        evolution_col_name='evolution_computed',
        how='left',
        fillna=None
):
    """
    Compute an evolution column against a period distant from a fixed
    frequency.

    Unfortunately, pandas doesn't allow .change() and .pct_change() to be
    executed with a MultiIndex.

    Args:
        df (pd.DataFrame):
        id_cols (list(str)):
        date_col (str):
        value_col (str):
        freq (int/pd.DateOffset/pd.Serie):
        method (str): default ``'abs'`` can be also ``'pct'``
        format(str): default 'column' can be also 'df'
        offseted_suffix(str): default '_offseted'
        evolution_col_name(str): default 'evolution_computed'
        how(str): default 'left'
        fillna(str/int): default None
    """

    if isinstance(freq, dict):
        freq = pd.DateOffset(**{k: int(v) for k, v in freq.items()})
        df[date_col + '_copy'] = df[date_col]
        df[date_col] = pd.to_datetime(df[date_col])

    df_offseted = df[id_cols + [date_col, value_col]].copy()
    df_offseted[date_col] += freq

    df_offseted_deduplicated = df_offseted.drop_duplicates(
        subset=id_cols + [date_col])

    if df_offseted_deduplicated.shape[0] != df_offseted.shape[0]:
        logging.getLogger(__name__).warning(
            "Warning: a dataframe for which you want to compute evolutions has"
            " duplicated values against the id_cols you indicated."
        )

    df_with_offseted_values = pd.merge(
        df,
        df_offseted_deduplicated,
        how=how,
        on=id_cols + [date_col],
        suffixes=['', offseted_suffix]
    ).reset_index(drop=True)

    if fillna is not None:
        df_with_offseted_values[[value_col, value_col + offseted_suffix]] = \
            df_with_offseted_values[
                [value_col, value_col + offseted_suffix]].fillna(fillna)

    if method == 'abs':
        df_with_offseted_values[evolution_col_name] = (
            df_with_offseted_values[value_col] -
            df_with_offseted_values[value_col + offseted_suffix]
        )
    elif method == 'pct':
        df_offseted_value_as_float = \
            df_with_offseted_values[value_col + offseted_suffix].astype(float)
        df_with_offseted_values[evolution_col_name] = (
            (df_with_offseted_values[value_col].astype(float) -
             df_offseted_value_as_float) / df_offseted_value_as_float
        )
    else:
        raise ValueError("method has to be either 'abs' or 'pct'")

    if format == 'df':
        return df_with_offseted_values
    else:
        return df_with_offseted_values[evolution_col_name]


def compute_cumsum(
        df,
        id_cols,
        reference_cols,
        value_cols,
        cols_to_keep=None
):
    """
    Compute cumsum for a group of columns.
    - `id_cols` are the columns id to create each group,
    - `reference_cols` are the columns to order the cumsum,
    - `value_cols` are the columns to cumsum,
    - `cols_to_keep` are other column to keep in the dataframe. This option can
     be used if there is only one row by group [id_cols + reference_cols]

    For example :

    MONTH  DAY NAME  VALUE  X
     1      1    A      1  lo
     2      1    A      1  lo
     2     15    A      1  la
     1     15    B      1  la

    The function `compute_cumsum` with the arguments :
            id_cols=['NAME']
            reference_cols=['MONTH','DAY']
            cumsum_cols=['VALUE']
            cols_to_keep=['X']
    give as a result :


    NAME  MONTH  DAY  X  VALUE
     A     1      1  lo      1
     A     2      1  la      2
     A     2     15  lo      3
     B     1     15  la      1


    Args:
        df (pd.DataFrame):
        id_cols (list(str)):
        reference_cols (list(str)):
        value_cols (list(str)):
        cols_to_keep (list(str))
    """
    if cols_to_keep is None:
        cols_to_keep = []
    levels = list(range(0, len(id_cols)))

    df = df.groupby(id_cols + reference_cols + cols_to_keep).sum()
    df = df.groupby(level=levels)[value_cols].cumsum().reset_index()

    return df


def add_missing_row(df, id_cols, reference_col, complete_index=None):
    """
    Add missing row to a df base on a reference column
    - `id_cols` are the columns id to group,
    - `reference_col` is the column with groups missing values
    - `complete_index` (optional) a set of values used to add missing rows,
      by default use the function `unique` on reference_col

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
    """
    names = id_cols + [reference_col]
    new_df = df.set_index(names)
    index = df.groupby(id_cols).sum().index
    if complete_index is None:
        complete_index = sorted(df[reference_col].unique())
    new_tuples_index = [x + (y,) for x in index.values for y in complete_index]

    new_index = pd.MultiIndex.from_tuples(new_tuples_index, names=names)
    return new_df.reindex(new_index).reset_index()


def compute_ffill_by_group(df, id_cols, reference_cols, value_col):
    """
    Compute ffill with groupby. There is a performance issue with a simple
    groupby/fillna (2017/07)
    - `id_cols` are the columns id to group,
    - `reference_cols` are the other columns used to order,
    - `value_col` is the name of the column to fill,

    Args:
        df (pd.DataFrame):
        id_cols (list(str)):
        reference_cols (list(str)):
        value_col (str):
    """
    df = df.set_index(id_cols).sort_index().sort_values(by=reference_cols)
    df['fill'] = 1 - df[value_col].isnull().astype(int)
    df['fill'] = df.groupby(
        level=list(range(0, len(id_cols) - 1))
    )['fill'].cumsum()
    df[value_col] = df[value_col].ffill()
    df.loc[df['fill'] == 0, value_col] = None
    del df['fill']
    return df.reset_index()
