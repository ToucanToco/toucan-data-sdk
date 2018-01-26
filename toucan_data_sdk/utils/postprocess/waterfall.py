import pandas as pd


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
