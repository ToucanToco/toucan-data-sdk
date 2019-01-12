from typing import Dict, List, Union

GroupCols = Union[str, List[str]]
Agg = Dict[str, str]  # dict of size 1: mapping colomn -> aggregation function


def _groupby_inplace(df, group_cols: GroupCols, aggregations: Agg):
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
    df = df.groupby(group_cols, as_index=False).agg(aggregations)
    return df


def _groupby_append(df, group_cols: GroupCols, aggregations: Dict[str, Agg]):
    """
    df =
       year  group libelle      mois  value  total
    0  2018  e-EKO       a  20180101      3      3
    1  2018  e-EKO       b  20180101      0      3
    2  2018  e-EKO       c  20180101      4      7
    3  2018    DOQ       q  20180101     33     33
    4  2018    DOQ       b  20180101     54     87
    5  2018     DO       q  20180101     13     13
    6  2018     DO       c  20180101     14     27

    df = groupby_append(
        df,
        ['mois', 'group'],
        {
            'max_total': {'total': 'max'},
            'sum_total': {'total': 'sum'},
            'mean_value': {'value': 'mean'}
        }
    )

    df =
       year  group libelle      mois  value  total  max_total  sum_total  mean_value
    0  2018  e-EKO       a  20180101      3      3          7         13    2.333333
    1  2018  e-EKO       b  20180101      0      3          7         13    2.333333
    2  2018  e-EKO       c  20180101      4      7          7         13    2.333333
    3  2018    DOQ       q  20180101     33     33         87        120   43.500000
    4  2018    DOQ       b  20180101     54     87         87        120   43.500000
    5  2018     DO       q  20180101     13     13         27         40   13.500000
    6  2018     DO       c  20180101     14     27         27         40   13.500000
    """
    group = df.groupby(group_cols)
    for new_col, aggs in aggregations.items():
        assert len(aggs) == 1
        (col, agg), *_ = aggs.items()
        df[new_col] = group[col].transform(agg)
    return df


def groupby(df, *, group_cols: GroupCols, aggregations: Union[Agg, Dict[str, Agg]]):
    if all(isinstance(a, dict) for a in aggregations.values()):
        return _groupby_append(df, group_cols, aggregations)
    else:
        return _groupby_inplace(df, group_cols, aggregations)
