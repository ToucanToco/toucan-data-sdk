import logging

import pandas as pd

from toucan_data_sdk.utils.helpers import check_params_columns_duplicate


def compute_evolution_by_frequency(
    df,
    id_cols,
    date_col,
    value_col,
    freq=1,
    method='abs',
    format='column',
    offseted_suffix='_offseted',
    evolution_col_name='evolution_computed',
    missing_date_as_zero=False,
    raise_duplicate_error=True
):
    if missing_date_as_zero:
        how = 'outer'
        fillna = 0
    else:
        how = 'left'
        fillna = None

    return __compute_evolution(
        df=df,
        id_cols=id_cols,
        value_col=value_col,
        date_col=date_col,
        freq=freq,
        method=method,
        format=format,
        offseted_suffix=offseted_suffix,
        evolution_col_name=evolution_col_name,
        how=how,
        fillna=fillna,
        raise_duplicate_error=raise_duplicate_error
    )


def compute_evolution_by_criteria(
    df,
    id_cols,
    value_col,
    compare_to,
    method='abs',
    format='column',
    offseted_suffix='_offseted',
    evolution_col_name='evolution_computed',
    raise_duplicate_error=True
):
    return __compute_evolution(**locals())


# old name
compute_evolution = compute_evolution_by_frequency


def __compute_evolution(
    df,
    id_cols,
    value_col,
    date_col=None,
    freq=1,
    compare_to=None,
    method='abs',
    format='column',
    offseted_suffix='_offseted',
    evolution_col_name='evolution_computed',
    how='left',
    fillna=None,
    raise_duplicate_error=True
):
    """
    Compute an evolution column :
        - against a period distant from a fixed frequency.
        - against a part of the df

    Unfortunately, pandas doesn't allow .change() and .pct_change() to be
    executed with a MultiIndex.

    Args:
        df (pd.DataFrame):
        id_cols (list(str)):
        value_col (str):
        date_col (str): default None
        freq (int/pd.DateOffset/pd.Serie): default 1
        compare_to (str): default None
        method (str): default ``'abs'`` can be also ``'pct'``
        format(str): default 'column' can be also 'df'
        offseted_suffix(str): default '_offseted'
        evolution_col_name(str): default 'evolution_computed'
        how(str): default 'left'
        fillna(str/int): default None
    """
    check_params_columns_duplicate(id_cols + [value_col, date_col])
    use_date_frequency = date_col is not None
    is_freq_dict = isinstance(freq, dict)
    if use_date_frequency:
        if is_freq_dict:
            freq = pd.DateOffset(**{k: int(v) for k, v in freq.items()})
            df[date_col + '_copy'] = df[date_col]
            df[date_col] = pd.to_datetime(df[date_col])
        group_cols = id_cols + [date_col]
        df_offseted = df[group_cols + [value_col]].copy()
        df_offseted[date_col] += freq
    elif compare_to is not None:
        group_cols = id_cols
        df_offseted = df.query(compare_to).copy()
        df_offseted = df_offseted[group_cols + [value_col]]

    df_offseted_deduplicated = df_offseted.drop_duplicates(subset=group_cols)

    if df_offseted_deduplicated.shape[0] != df_offseted.shape[0] and how == 'left':
        msg = ("A dataframe for which you want to compute evolutions "
               "has duplicated values against the id_cols you indicated.")
        if raise_duplicate_error:
            raise DuplicateRowsError(msg)
        else:
            logging.getLogger(__name__).warning(f"Warning: {msg}")

    df_with_offseted_values = pd.merge(
        df,
        df_offseted_deduplicated,
        how=how,
        on=group_cols,
        suffixes=['', offseted_suffix]
    ).reset_index(drop=True)

    if fillna is not None:
        df_with_offseted_values[[value_col, value_col + offseted_suffix]] = \
            df_with_offseted_values[[value_col, value_col + offseted_suffix]].fillna(fillna)

    if use_date_frequency and is_freq_dict:
        df_with_offseted_values[date_col] = df_with_offseted_values[date_col + '_copy']
        del df_with_offseted_values[date_col + '_copy']

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
             df_offseted_value_as_float) /
            df_offseted_value_as_float
        )
    else:
        raise ValueError("method has to be either 'abs' or 'pct'")

    if format == 'df':
        return df_with_offseted_values
    else:
        return df_with_offseted_values[evolution_col_name]


class DuplicateRowsError(Exception):
    """Raised if a dataframe has duplicate rows"""
