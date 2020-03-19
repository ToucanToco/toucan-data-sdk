from typing import Any, List

import numpy as np
import pandas as pd

__all__ = (
    'lower',
    'upper',
    'title',
    'capitalize',
    'swapcase',
    'length',
    'isalnum',
    'isalpha',
    'isdigit',
    'isspace',
    'islower',
    'isupper',
    'istitle',
    'isnumeric',
    'isdecimal',
    'strip',
    'lstrip',
    'rstrip',
    'center',
    'ljust',
    'rjust',
    'split',
    'rsplit',
    'partition',
    'rpartition',
    'find',
    'rfind',
    'index',
    'rindex',
    'startswith',
    'endswith',
    'concat',
    'contains',
    'repeat',
    'replace_pattern',
    # 'slice',
    # 'slice_replace',
    # 'count'
)


###################################################################################################
#                              METHODS WITH NO EXTRA PARAMETERS
#
# All these functions have the same signature:
# :param df: the dataframe
# :param column: the column
# :param new_column: the destination column (if not set, `column` will be used)
# :return: the transformed dataframe
###################################################################################################


def _generate_basic_str_postprocess(method_name, docstring):
    def f(df, column: str, new_column: str = None):
        method = getattr(df[column].str, method_name)
        new_column = new_column or column
        df.loc[:, new_column] = method()
        return df

    f.__name__ = method_name
    f.__doc__ = f"""
    {docstring}
    See [pandas doc](
    https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.str.{method_name}.html) for more information

    ---

    ### Parameters

    *mandatory :*
    - `column` (*str*): the column

    *optional :*
    - `new_column` (*str*): the destination column (if not set, `column` will be used)
    """
    return f


doc = 'Compute length of each string of `column`'
length = _generate_basic_str_postprocess('len', doc)

# lower, upper, capitalize, title, swapcase
###################################################################################################
doc = 'Converts all characters of `column` to lowercase.'
lower = _generate_basic_str_postprocess('lower', doc)

doc = 'Converts all characters of `column` to uppercase.'
upper = _generate_basic_str_postprocess('upper', doc)

doc = (
    'Converts first character to uppercase and remaining ' 'to lowercase for each line of `column`.'
)
capitalize = _generate_basic_str_postprocess('capitalize', doc)

doc = (
    'Converts first character to uppercase and remaining '
    'to lowercase for each word of each line of `column`.'
)
title = _generate_basic_str_postprocess('title', doc)

doc = 'Converts uppercase to lowercase and lowercase to uppercase for each word of `column`.'
swapcase = _generate_basic_str_postprocess('swapcase', doc)

# isalnum, isalpha, isdigit, isspace, islower, isupper, istitle, isnumeric, isdecimal
###################################################################################################
doc = 'Check whether all characters in each string in `column` are alphanumeric'
isalnum = _generate_basic_str_postprocess('isalnum', doc)

doc = 'Check whether all characters in each string in `column` are alphabetic'
isalpha = _generate_basic_str_postprocess('isalpha', doc)

doc = 'Check whether all characters in each string in `column` are digits'
isdigit = _generate_basic_str_postprocess('isdigit', doc)

doc = 'Check whether all characters in each string in `column` are whitespace'
isspace = _generate_basic_str_postprocess('isspace', doc)

doc = 'Check whether all characters in each string in `column` are lowercase'
islower = _generate_basic_str_postprocess('islower', doc)

doc = 'Check whether all characters in each string in `column` are uppercase'
isupper = _generate_basic_str_postprocess('isupper', doc)

doc = 'Check whether all characters in each string in `column` are titlecase'
istitle = _generate_basic_str_postprocess('istitle', doc)

doc = 'Check whether all characters in each string in `column` are numeric'
isnumeric = _generate_basic_str_postprocess('isnumeric', doc)

doc = 'Check whether all characters in each string in `column` are decimal'
isdecimal = _generate_basic_str_postprocess('isdecimal', doc)


###################################################################################################
#                                        STRIP METHODS
#
# All these functions have the same signature:
# :param df: the dataframe
# :param column: the column
# :param to_strip: (str: None) set of characters to be removed
# :param new_column: the destination column (if not set, `column` will be used)
# :return: the transformed dataframe
###################################################################################################
def _generate_strip_str_postprocess(method_name, docstring):
    def f(df, column: str, *, to_strip: str = None, new_column: str = None):
        method = getattr(df[column].str, method_name)
        new_column = new_column or column
        df.loc[:, new_column] = method(to_strip)
        return df

    f.__name__ = method_name
    f.__doc__ = f"""
    {docstring}
    See [pandas doc](
    https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.str.{method_name}.html) for more information

    ---

    ### Parameters

    *mandatory :*
    - `column` (*str*): the column

    *optional :*
    - `to_strip` (*str*): set of characters to be removed
    - `new_column` (*str*): the destination column (if not set, `column` will be used)
    """
    return f


doc = 'Strip whitespace (including newlines) from each string in `column` from both sides'
strip = _generate_strip_str_postprocess('strip', doc)

doc = 'Strip whitespace (including newlines) from each string in `column` from left side'
lstrip = _generate_strip_str_postprocess('lstrip', doc)

doc = 'Strip whitespace (including newlines) from each string in `column` from left side'
rstrip = _generate_strip_str_postprocess('rstrip', doc)


###################################################################################################
#                              METHODS with `width` and `fillchar`
#
# All these functions have the same signature:
# :param df: the dataframe
# :param column: the column
# :param width: (int) minimum width
# :param fillchar: (default: \' \') additional character for filling
# :param new_column: the destination column (if not set, `column` will be used)
# :return: the transformed dataframe
###################################################################################################


def _generate_width_str_postprocess(method_name, docstring):
    def f(df, column: str, *, width: int, fillchar: str = ' ', new_column: str = None):
        method = getattr(df[column].str, method_name)
        new_column = new_column or column
        df.loc[:, new_column] = method(width, fillchar=fillchar)
        return df

    f.__name__ = method_name
    f.__doc__ = f"""
    {docstring}
    See [pandas doc](
    https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.str.{method_name}.html) for more information

    ---

    ### Parameters

    *mandatory :*
    - `column` (*str*): the column
    - `width` (*int*): minimum widt

    *optional :*
    - `fillchar` (*str*): additional character for filling
    - `new_column` (*str*): the destination column (if not set, `column` will be used)
    """
    return f


doc = 'Filling left and right side of strings in `column` with an additional character'
center = _generate_width_str_postprocess('center', doc)

doc = 'Filling right side of strings in `column` with an additional character'
ljust = _generate_width_str_postprocess('ljust', doc)

doc = 'Filling left side of strings in `column` with an additional character'
rjust = _generate_width_str_postprocess('rjust', doc)


###################################################################################################
#                                        SPLIT METHODS
#
# All these functions have the same signature:
# :param df: the dataframe
# :param column: the column
# :param new_columns: the destination columns
#        (if not set, columns `column_1`, ..., `column_n` will be created)
# :param sep: (default: \' \') string or regular expression to split on
# :param limit: (default: None) limit number of splits in output
# :return: the transformed dataframe
###################################################################################################
def _generate_split_str_postprocess(method_name, docstring):
    def f(df, column: str, *, new_columns: List[str] = None, sep: str = ' ', limit: int = None):
        method = getattr(df[column].str, method_name)
        df_split = method(pat=sep, n=limit, expand=True)
        nb_cols = df_split.shape[1]
        if new_columns and (not isinstance(new_columns, list) or nb_cols > len(new_columns)):
            raise ValueError(f"'new_columns' should be a list with at least {nb_cols} elements")
        if new_columns is None:
            new_columns = [f'{column}_{i}' for i in range(1, nb_cols + 1)]
        df[new_columns[:nb_cols]] = df_split
        return df

    f.__name__ = method_name
    f.__doc__ = f"""
    {docstring}
    See [pandas doc](
    https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.str.{method_name}.html) for more information

    ---

    ### Parameters

    *mandatory :*
    - `column` (*str*): the column

    *optional :*
    - `sep` (*str*): string or regular expression to split on
    - `limit` (*int*): limit number of splits in output (by default, there is no limit)
    - `new_columns` (*list*): the destination columns (by default, new columns will be added automatically)
    """
    return f


doc = 'Split each string in the caller’s values by given pattern, propagating NaN values'
split = _generate_split_str_postprocess('split', doc)

doc = (
    'Split each string `column` by the given delimiter string, '
    'starting at the end of the string and working to the front'
)
rsplit = _generate_split_str_postprocess('rsplit', doc)


###################################################################################################
#                                        PARTITION METHODS
#
# All these functions have the same signature:
# :param df: the dataframe
# :param column: the column
# :param new_columns: the 3 destination columns
# :param sep: (default: \' \') string or regular expression to split on
# :return: the transformed dataframe
###################################################################################################
def _generate_partition_str_postprocess(method_name, docstring):
    def f(df, column: str, *, new_columns: List[str], sep: str = ' '):
        if len(new_columns) != 3:
            raise ValueError('`new_columns` must have 3 columns exactly')
        method = getattr(df[column].str, method_name)
        df[new_columns] = method(sep)
        return df

    f.__name__ = method_name
    f.__doc__ = f"""
    {docstring}
    See [pandas doc](
    https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.str.{method_name}.html) for more information

    ---

    ### Parameters

    *mandatory :*
    - `column` (*str*): the column
    - `new_columns` (*list*): the 3 destination columns

    *optional :*
    - `sep` (*str*): string or regular expression to split on
    """
    return f


doc = (
    'Split the string at the first occurrence of sep, and return 3 elements containing '
    'the part before the separator, the separator itself, and the part after the separator. '
    'If the separator is not found, return 3 elements containing the string itself, '
    'followed by two empty strings.'
)
partition = _generate_partition_str_postprocess('partition', doc)

doc = (
    'Split the string at the last occurrence of sep, and return 3 elements containing '
    'the part before the separator, the separator itself, and the part after the separator. '
    'If the separator is not found, return 3 elements containing two empty strings, '
    'followed by the string itself.'
)
rpartition = _generate_partition_str_postprocess('rpartition', doc)


###################################################################################################
#                                   INDEX AND FIND METHODS
#
# All these functions have the same signature:
# :param df: the dataframe
# :param column: the column
# :param new_column: the destination column (if not set, `column` will be used)
# :param sub: substring being searched
# :param start: (default: 0) left edge index
# :param end: (default: None) right edge index
# :return: the transformed dataframe
###################################################################################################
def _generate_find_str_postprocess(method_name, docstring):
    def f(df, column: str, *, sub: str, start: int = 0, end: int = None, new_column: str = None):
        method = getattr(df[column].str, method_name)
        new_column = new_column or column
        df.loc[:, new_column] = method(sub, start, end)
        return df

    f.__name__ = method_name
    f.__doc__ = f"""
    {docstring}
    See [pandas doc](
    https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.str.{method_name}.html) for more information

    ---

    ### Parameters

    *mandatory :*
    - `column` (*str*): the column
    - `sub` (*str*): substring being searched

    *optional :*
    - `start` (*int*): left edge index
    - `end` (*int*): right edge index
    - `new_column` (*str*): the destination column (if not set, `column` will be used)
    """
    return f


doc = (
    'Return lowest indexes in each strings in `column` where the substring '
    'is fully contained between [start:end]. Return -1 on failure'
)
find = _generate_find_str_postprocess('find', doc)

doc = (
    'Return highest indexes in each strings in `column` where the substring '
    'is fully contained between [start:end]. Return -1 on failure'
)
rfind = _generate_find_str_postprocess('rfind', doc)

doc = (
    'Return lowest indexes in each strings where the substring is fully contained '
    'between [start:end]. This is the same as str.find except instead of returning -1, '
    'it raises a ValueError when the substring is not found'
)
index = _generate_find_str_postprocess('index', doc)

doc = (
    'Return highest indexes in each strings where the substring is fully contained '
    'between [start:end]. This is the same as str.find except instead of returning -1, '
    'it raises a ValueError when the substring is not found'
)
rindex = _generate_find_str_postprocess('rindex', doc)


###################################################################################################
#                                  STARTSWITH/ENDSWITH METHODS
#
# All these functions have the same signature:
# :param df: the dataframe
# :param column: the column
# :param new_column: the destination column (if not set, `column` will be used)
# :param pat: character sequence
# :param na: (default: NaN) object shown if element tested is not a string
# :return: the transformed dataframe
###################################################################################################
def _generate_with_str_postprocess(method_name, docstring):
    def f(df, column: str, *, pat: str, na: Any = np.nan, new_column: str = None):
        method = getattr(df[column].str, method_name)
        new_column = new_column or column
        df.loc[:, new_column] = method(pat, na=na)
        return df

    f.__name__ = method_name
    f.__doc__ = (
        f'{docstring}\n'
        f':param df: the dataframe\n'
        f':param column: the column\n'
        f':param new_column: the destination column (if not set, `column` will be used)\n'
        f':param pat: character sequence\n'
        f':param na: (default: NaN) object shown if element tested is not a string\n'
        f':return: the transformed dataframe'
    )
    f.__doc__ = f"""
    {docstring}
    See [pandas doc](
    https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.str.{method_name}.html) for more information

    ---

    ### Parameters

    *mandatory :*
    - `column` (*str*): the column
    - `pat` (*str*): character sequence

    *optional :*
    - `na`: object shown if element tested is not a string
    - `new_column` (*str*): the destination column (if not set, `column` will be used)
    """
    return f


doc = 'Test if the start of each string element matches a pattern.'
startswith = _generate_with_str_postprocess('startswith', doc)

doc = 'Test if the end of each string element matches a pattern.'
endswith = _generate_with_str_postprocess('endswith', doc)


###################################################################################################
#                                        OTHER METHODS
###################################################################################################
def concat(df, *, columns: List[str], new_column: str, sep: str = None):
    """
    Concatenate `columns` element-wise
    See [pandas doc](
    https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.str.cat.html) for more information

    ---

    ### Parameters

    *mandatory :*
    - `columns` (*list*): list of columns to concatenate (at least 2 columns)
    - `new_column` (*str*): the destination column

    *optional :*
    - `sep` (*str*): the separator
    """
    if len(columns) < 2:
        raise ValueError('The `columns` parameter needs to have at least 2 columns')
    first_col, *other_cols = columns

    def is_integer_column(df: pd.DataFrame, column: str):
        """Check if a column has only integers or NaN"""
        try:
            return all(pd.isnull(x) or x.is_integer() for x in df[column])
        except Exception:
            return False

    str_sub_df = df[columns]
    for col in columns:
        # In case of integer columns, we don't want the values to be considered
        # as floats (with leading `.0` because of NaN values)
        if is_integer_column(str_sub_df, col):
            str_sub_df[col] = str_sub_df[col].apply(lambda x: '' if pd.isnull(x) else int(x))
        str_sub_df[col] = str_sub_df[col].astype(str)

    df.loc[:, new_column] = str_sub_df[first_col].str.cat(str_sub_df[other_cols], sep=sep)
    return df


def contains(
    df,
    column: str,
    *,
    pat: str,
    new_column: str = None,
    case: bool = True,
    na: Any = None,
    regex: bool = True,
):
    """
    Test if pattern or regex is contained within strings of `column`
    See [pandas doc](
    https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.str.contains.html) for more information

    ---

    ### Parameters

    *mandatory :*
    - `column` (*str*): the column
    - `pat` (*str*): character sequence or regular expression.

    *optional :*
    - `new_column` (*str*): the destination column (if not set, `column` will be used)
    - `case` (*boolean*): if true, case sensitive.
    - `na`: fill value for missing values.
    - `regex` (*boolean*): default true
    """
    new_column = new_column or column
    df.loc[:, new_column] = df[column].str.contains(pat, case=case, na=na, regex=regex)
    return df


def repeat(df, column: str, *, times: int, new_column: str = None):
    """
    Duplicate each string in `column` by indicated number of time
    See [pandas doc](
    https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.str.repeat.html) for more information

    ---

    ### Parameters

    *mandatory :*
    - `column` (*str*): the column
    - `times` (*int*): times to repeat the string

    *optional :*
    - `new_column` (*str*): the destination column (if not set, `column` will be used)
    """
    new_column = new_column or column
    df.loc[:, new_column] = df[column].str.repeat(times)
    return df


def replace_pattern(
    df,
    column: str,
    *,
    pat: str,
    repl: str,
    new_column: str = None,
    case: bool = True,
    regex: bool = True,
):
    """
    Replace occurrences of pattern/regex in `column` with some other string
    See [pandas doc](
    https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.str.replace.html) for more information

    ---

    ### Parameters

    *mandatory :*
    - `column` (*str*): the column
    - `pat` (*str*): character sequence or regular expression
    - `repl` (*str*): replacement string

    *optional :*
    - `new_column` (*str*): the destination column (if not set, `column` will be used)
    - `case` (*boolean*): if true, case sensitive.
    - `regex` (*boolean*): default true
    """
    new_column = new_column or column
    df.loc[:, new_column] = df[column].str.replace(pat, repl, case=case, regex=regex)
    return df
