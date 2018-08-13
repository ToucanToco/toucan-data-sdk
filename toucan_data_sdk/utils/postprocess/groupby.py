from toucan_data_sdk.utils.helpers import ParamsValueError


def groupby(df, group_cols=None, aggregations=None):
    """
    Aggregate values by groups.

    :param df: dataframe to group
    :param group_cols: list of columns used to group data
    :param aggregations: dictionnary of values columns to group as keys and aggregation function to
        use as values. Available aggregation functions:
         - 'sum'
         - 'mean'
         - 'median'
         - 'prod' (product)
         - 'std' (standard deviation)
         - 'var' (variance)
    :return: the summarized dataframe

    Example:

    Input df:

    | ENTITY | YEAR | VALUE_1 | VALUE_2 |
    |:------:|:----:|:-------:|:-------:|
    |    A   | 2017 |    10   |    3    |
    |    A   | 2017 |    20   |    1    |
    |    A   | 2018 |    10   |    5    |
    |    A   | 2018 |    30   |    4    |
    |    B   | 2017 |    60   |    4    |
    |    B   | 2017 |    40   |    3    |
    |    B   | 2018 |    50   |    7    |
    |    B   | 2018 |    60   |    6    |

    groupby(
        df=data,
        group_cols=['ENTITY', 'YEAR'],
        aggregations={
            'VALUE_1': 'sum',
            'VALUE_2': 'mean'
        }
    )

    returns:

    | ENTITY | YEAR | VALUE_1 | VALUE_2 |
    |:------:|:----:|:-------:|:-------:|
    |    A   | 2017 |    30   |   2.0   |
    |    A   | 2018 |    40   |   4.5   |
    |    B   | 2017 |   100   |   3.5   |
    |    B   | 2018 |   110   |   6.5   |

    """
    if group_cols is None:
        raise ParamsValueError("You have to provide the 'group_cols' parameter with a list of at "
                               "least one column on which to group data ('group_cols')")
    if aggregations is None:
        raise ParamsValueError("You have to provide the 'aggregations' parameter with a dictionnary"
                               "of at least a value column as key and an aggregation function as "
                               "value (among sum, mean, median, prod, std, var)")
    df = df.groupby(group_cols, as_index=False).agg(aggregations)
    return df
