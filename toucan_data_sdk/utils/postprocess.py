import numpy as np
import pandas as pd


def replace(df, column, dst_column=None, **kwargs):
    """
    Replace values of a column (uses pandas.Series.replace)
    Args:
        df (pd.DataFrame): DataFrame to transform
        column (str): name of the column containing values to replace
        dst_column (str): optional, name of the column which will contain replaced
                          values (same as "column" by default)

        Other parameters are directly forwarded to pandas.Series.replace.
    """
    dst_column = dst_column or column
    df.loc[:, dst_column] = df[column].replace(**kwargs)
    return df


def rename(df, values=None, columns=None, locale=None):
    """
    Replaces data values and column names according to locale
    Args:
        df (pd.DataFrame): DataFrame to transform
        values (dict):
            - key (str): term to be replaced
            - value (dict):
                - key: locale
                - value: term's translation
        columns (dict):
            - key (str): columns name to be replaced
            - value (dict):
                - key: locale
                - value: column name's translation
        locale (str): locale
    """
    if values:
        to_replace = list(values.keys())
        value = [values[term][locale] for term in values]
        df = df.replace(to_replace=to_replace, value=value)
    if columns:
        _keys = list(columns.keys())
        _values = [column[locale] for column in columns.values()]
        columns = dict(list(zip(_keys, _values)))
        df = df.rename(columns=columns)
    return df


def melt(df, id, value, dropna=False):
    """
    This function is useful to massage a DataFrame into a format where one or more columns
    are identifier variables (id), while all other columns,
    considered measured variables (value), are “unpivoted” to the row axis,
    leaving just two non-identifier columns, ‘variable’ and ‘value’.
    Args:
        df (pd.DataFrame): DataFrame to transform
        id (list): Column(s) to use as identifier variables
        value (list): Column(s) to unpivot.
        dropna (bool): dropna in added 'value' column
    """
    try:
        df = df[(id + value)]
        df = pd.melt(df, id_vars=id, value_vars=value)
        if dropna:
            df = df.dropna(subset=['value'])
    except KeyError as e:
        raise Exception(f'Invalid configuration for melt, missing key: {e}')
    else:
        return df


def top(df, value, limit, order='asc', group=None):
    """
    Awesome method that achieves what NO query in any language can do: (DRUM ROLL)
    Get the top or flop N results based on a column value for each specified group columns
    Args:
        - group: String or array of strings for the columns,
                 on which you want to perform the group operation
        - value: String for the column name on which you will rank the results
        - order: String 'asc' or 'desc' to sort by ascending ou descending order
        - limit: Number to specify the N results you want to retrieve.
                 Use a positive number x to retrieve the first x results.
                 Use a negative number -x to retrieve the last x results.
    """
    ascending = order != 'desc'
    limit = int(limit)
    filter_func = 'nlargest' if (limit > 0) ^ ascending else 'nsmallest'

    def _top(df):
        return getattr(df, filter_func)(abs(limit), value).sort_values(by=value,
                                                                       ascending=ascending)

    try:
        if group is None:
            df = _top(df)
        else:
            df = df.groupby(group).apply(_top)
    except KeyError as e:
        raise Exception(f'Invalid configuration for top, missing key: {e}')
    else:
        return df


def pivot(df, index, column, value):
    """
    Pivot a dataframe. Reverse operation of melting. Useful for configuring evolution
    See pandas' pivot_table documentation for more details
    Args:
        - index (list): indexes argument of pd.pivot_table
        - column (str): column name to pivot on
        - value (str): column name containing the value to fill the pivoted df
    """
    try:
        if df.dtypes[value].type == np.object_:
            df = pd.pivot_table(df, index=index,
                                columns=column,
                                values=value,
                                aggfunc=lambda x: ' '.join(x))
        else:
            df = pd.pivot_table(df, index=index,
                                columns=column,
                                values=value)
        df = df.reset_index()
    except KeyError as e:
        raise Exception(f'Invalid configuration for pivot, missing key: {e}')
    else:
        return df


def pivot_by_group(df, variable, value, new_columns, groups, id_cols=None):
    if id_cols is None:
        index = [variable]
    else:
        index = [variable] + id_cols

    param = pd.DataFrame(groups, index=new_columns)
    temporary_colum = 'tmp'

    df[temporary_colum] = df[variable]
    for column in param.columns:
        df.loc[df[variable].isin(param[column]), variable] = column

    param = param.T
    for column in param.columns:
        df.loc[
            df[temporary_colum].isin(param[column]), temporary_colum] = column

    df = pivot(df, index, temporary_colum, value)
    return df


def argmax(df, column):
    df = df[df[column] == df[column].max()]
    return df


def fillna(df, column, value):
    """
    Can fill NaN values from a column
    Args:
        df
        column
        value
    """
    if column in df.columns:
        df[column] = df[column].fillna(value)
    else:
        df[column] = value
    return df


def query_df(df, query):
    """
    Slice the data according to the provided query
    Basic usage like the one in the data query but in the postprocess
    Useful if you want to perform some slicing after a melt or pivot for example.
    Wired on the DataFrame.query method, see doc
    http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.query.html#pandas.DataFrame.query
    Args:
        Query String
    """
    try:
        df = df.query(query)
    except Exception as e:
        raise Exception(f'Invalid query: {e}')
    else:
        return df


def add(df, new_column, column_1, column_2):
    """
    Basic mathematical operation to add column_1 and column_2 values.
    Will create a new column named `new_column`
    """
    try:
        df[new_column] = df[column_1] + df[column_2]
    except KeyError as e:
        raise Exception(f'Invalid config for sum: {e}')
    else:
        return df


def subtract(df, new_column, column_1, column_2):
    """
    Basic mathematical operation to substract column_2 to column_1 values.
    Will create a new column named `new_column`
    """
    try:
        df[new_column] = df[column_1] - df[column_2]
    except KeyError as e:
        raise Exception(f'Invalid config for subtract: {e}')
    else:
        return df


def multiply(df, new_column, column_1, column_2):
    """
    Basic mathematical operation to multiply column_1 and column_2 values.
    Will create a new column named `new_column`
    """
    try:
        df[new_column] = df[column_1] * df[column_2]
    except KeyError as e:
        raise Exception(f'Invalid config for multiply: {e}')
    else:
        return df


def divide(df, new_column, column_1, column_2):
    """
    Basic mathematical operation to divide column_2 to column_1 values.
    Will create a new column named `new_column`
    """
    try:
        df[new_column] = df[column_1] / df[column_2]
    except KeyError as e:
        raise Exception(f'Invalid config for divide: {e}')
    else:
        return df


def cumsum(df, new_column, column, index, date_column, date_format):
    """
    Creates a new column, which is the cumsum of the column
    :param df: the dataframe
    :param new_column: name of the new column
    :param column: name on which the cumulative sum is performed
    :param index: array of column names to keep as indices
    :param date_column: column name that represent the date
    :param date_format: format of the date
    :return:
    """
    date_temp = 'date_temp_'
    if isinstance(index, str):
        index = [index]
    try:
        df[date_temp] = pd.to_datetime(df[date_column], format=date_format)
        df2 = (df.groupby(index)
               .apply(lambda x: x.set_index(date_temp)
                      .sort_index()[[column]]
                      .cumsum())
               .reset_index()
               .rename(columns={column: new_column})
               )
        if new_column == column:
            df.drop(column, axis=1, inplace=True)
        df = df.merge(df2, on=[*index, date_temp]).drop(date_temp, axis=1)
    except KeyError as e:
        raise Exception(f'Invalid config for cumsum: {e}')
    else:
        return df


def percentage(df, new_column, column, group_cols=None):
    """
    Add a column to the dataframe according to the groupby logic on group_cols
    :param df: Dataframe
    :param new_column: name of the new column
    :param column: name of the desired column you need percentage on
    :param group_cols: (str | list of str) or None
    :return: df + the percentage column
    """
    if group_cols is None:
        df[new_column] = 100. * df[column] / sum(df[column])
    else:
        df[new_column] = (df.groupby(group_cols)
                          .apply(lambda x: 100. * x[column] / sum(x[column]))
                          .sort_index(level=len(group_cols))
                          .reset_index()[column]
                          )
    return df


def waterfall(df, date, value, start, end, upperGroup,  # noqa:C901
              insideGroup=None, breakdown=None):
    """
    Return a line for each bars of a waterfall chart, totals, groups, subgroups.
    Compute the variation and variation rate for each line.

    Args:
        upperGroup (dict)
            - id: name of the column that contains upperGroups unique IDs
            - label: not required, text displayed under each upperGroups bars,
                     using ID when it's absent
            - groupsOrder: not required, order of upperGroups
        insideGroup (dict)
            - id: name of the column that contains insideGroups unique IDs
            - label: not required, text displayed under each insideGroups bars,
                     using ID when it's absent
            - groupsOrder: not required, order of insideGroups
        date (str): name of the column that id the period of each lines
        value (str): name of the column that contains the vaue for each lines
        start (dict):
            - label: text displayed under the first master column
            - date: value in the date col that id lines for the first period
        end (dict):
            - label: text displayed under the last master column
            - date: value in the date col that id lines for the second period
        breakdown (list) : (not implemented)
        # fillValues (bool): (case when false is not implemented)

    TODO:
        * idea to implement breakdown, call waterfall() on data filtered by filter.
        * crash gracefully if data or config is not coherent
        * il y aura des cols en trop: les gérer
    """

    def rename_or_create(group, group_name, name, target, default):
        """
        Rename or create standard columns for optional options
        """
        col_name = name.format(group_name)
        if not group.get(target):
            df[col_name] = default
        else:
            df.rename(columns={group[target]: col_name}, inplace=True)

    def first(x):
        return x.iloc[0]

    def compute_totals(totals):
        """
        Compute two dataframes with value for start and end
        Args:
            totals(dataframe):

        Returns: Dataframe, Dataframe

        """
        result = {}
        time_dict = {'start': start, 'end': end}
        for time_name, time in time_dict.items():
            if not totals[totals['date'] == time['id']].empty:
                value = totals.loc[
                    totals['date'] == time['id'], 'value'
                ].values[0]
            else:
                value = 0
            result[time_name] = pd.DataFrame([{
                'value': value,
                'label': time['label']
            }])
        return result['start'], result['end']

    def merge_df(df):
        """
        Compute diff value between start and end
        Args:
            df(dataframe):

        Returns: Dataframe

        """
        start_df, end_df = df[df['date'] == start_id], df.loc[df['date'] == end_id]
        df = start_df.merge(end_df,
                            on=['insideGroup', 'upperGroup',
                                'upperGroup_order',
                                'insideGroup_order', 'upperGroup_label',
                                'insideGroup_label'],
                            how='outer',
                            suffixes=('_start', '_end'), )

        # necessary before calculating variation
        df[['value_start', 'value_end']] = df[['value_start', 'value_end']].fillna(0)
        df['value'] = df['value_end'] - df['value_start']
        df.drop(['date_start', 'date_end', 'value_end'], axis=1, inplace=True)
        df.rename(columns={'upperGroup': 'groups'}, inplace=True)
        return df

    def compute_inside_group(df):
        """
        Compute inside Group
        Args:
            df(dataframe):

        Returns: Dataframe

        """
        inside_group = df.copy()
        inside_group['type'] = 'child'
        inside_group['variation'] = inside_group['value'] / inside_group['value_start']
        inside_group.drop(['upperGroup_label', 'insideGroup', 'value_start'],
                          axis=1, inplace=True)
        inside_group.rename(columns={'insideGroup_label': 'label'}, inplace=True)
        return inside_group

    def compute_upper_group(df):
        """
        Compute upperGroup
        Args:
            df (Dataframe):

        Returns: Dataframe

        """
        upper_group = df.groupby(['groups']).agg({
            'value': sum,
            'value_start': sum,
            'upperGroup_label': first,
            'upperGroup_order': first
        }).reset_index()
        upper_group['type'] = 'parent'
        upper_group['variation'] = upper_group['value'] / upper_group['value_start']
        upper_group.drop(['value_start'], axis=1, inplace=True)
        upper_group.rename(columns={'upperGroup_label': 'label'}, inplace=True)
        return upper_group

    if len(df) == 0:
        return df

    start_id, end_id = start['id'], end['id']

    if breakdown is not None:
        raise NotImplementedError(
            'We will add breakdown support on your request, please contact the devs')
    if insideGroup is None:
        raise NotImplementedError(
            'We will add support for upperGroup only on you request, please contact the devs')

    # prepare the dataframe with standard column names

    df = df.rename(columns={
        upperGroup['id']: 'upperGroup',
        insideGroup['id']: 'insideGroup',
        date: 'date',
        value: 'value'
    })
    groups_dict = {'upperGroup': upperGroup, 'insideGroup': insideGroup}
    for g_name, g in groups_dict.items():
        rename_or_create(g, g_name, '{}_label', 'label', df[g_name])
        rename_or_create(g, g_name, '{}_order', 'groupsOrder', pd.np.nan)

    agg_conf = {'value': sum}
    agg_conf.update({'{}_label'.format(col): first for col in groups_dict.keys()})
    agg_conf.update({'{}_order'.format(col): first for col in groups_dict.keys()})
    df = df.groupby([*groups_dict.keys(), 'date']).agg(agg_conf).reset_index()
    start, end = compute_totals(df.groupby('date').agg({'value': sum}).reset_index())

    df = merge_df(df)

    groups = pd.concat([
        compute_upper_group(df),
        compute_inside_group(df)
    ]).sort_values(
        by=['upperGroup_order', 'groups', 'type', 'insideGroup_order', 'label'],
        ascending=[True, True, False, True, True])
    ret = pd.concat([start, groups, end])

    # We don't need specific sorting orders by groups now
    ret.loc[ret['type'] == 'child', 'order'] \
        = ret.loc[ret['type'] == 'child', 'insideGroup_order']
    ret.loc[ret['type'] == 'parent', 'order'] \
        = ret.loc[ret['type'] == 'parent', 'upperGroup_order']
    ret.drop(['insideGroup_order', 'upperGroup_order'], axis=1, inplace=True)

    return ret

query = query_df
